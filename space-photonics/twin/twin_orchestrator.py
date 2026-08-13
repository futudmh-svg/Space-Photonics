"""
Digital Twin Orchestrator

Main simulation controller that integrates:
- VLEO satellite orbit propagation
- Hypersonic vehicle tracking
- OPA beam steering
- Ag-chalcogenide amplification
- Nested control loops (optical PLL + digital Kalman)
- Atmospheric channel (turbulence, scintillation)
- VLEO thermal environment
- Optical link budget
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from .opa_beamsteer import OPABeamSteerer, OPAConfig
from .agchalcogenide import AgChalcogenideAmplifier, AgChalcogenideConfig
from .orbit_target import VLEOPropagator, HypersonicVehicle, OrbitConfig, VehicleConfig
from .control_loop import NestedControlSystem, OpticalLoopConfig, DigitalLoopConfig
from .atmospheric_channel import AtmosphericChannel, AtmosphericConfig
from .thermal_model import VLEOThermalModel, VLEOThermalConfig


@dataclass
class TwinConfig:
    """Digital twin simulation configuration."""
    # Timing
    dt: float = 1e-6               # Simulation time step [s]
    log_interval: float = 1e-3     # Logging interval [s]
    
    # Optical
    tx_power: float = 1.0          # TX power [W]
    wavelength: float = 1550e-9    # Wavelength [m]
    tx_aperture: float = 0.1       # TX aperture [m]
    rx_aperture: float = 0.05      # RX aperture [m]
    
    # Atmospheric
    atmospheric_loss_db: float = 2.0  # Clear sky loss
    scintillation_index: float = 0.1  # Log-amplitude variance
    
    # Tracking
    enable_tracking: bool = True
    tracking_bandwidth: float = 1e3   # Tracking loop bandwidth [Hz]
    pointing_loss_db: float = 3.0     # Initial pointing loss [dB]
    
    # Thermal
    enable_thermal: bool = True
    
    # Control
    enable_nested_control: bool = True


class DigitalTwin:
    """
    Space Photonics Digital Twin.
    
    Simulates the complete optical communication link from
    VLEO satellite to hypersonic vehicle with all-optical
    signal processing.
    """
    
    def __init__(self, config: Optional[TwinConfig] = None):
        self.cfg = config or TwinConfig()
        self.time = 0.0
        
        # Initialize subsystems
        self.satellite = VLEOPropagator(OrbitConfig())
        self.vehicle = HypersonicVehicle(VehicleConfig())
        self.opa = OPABeamSteerer(OPAConfig(wavelength=self.cfg.wavelength))
        self.amplifier = AgChalcogenideAmplifier(AgChalcogenideConfig())
        
        # Nested control system
        if self.cfg.enable_nested_control:
            self.control = NestedControlSystem(
                OpticalLoopConfig(bandwidth=1e9),
                DigitalLoopConfig(sample_rate=1/self.cfg.log_interval)
            )
        else:
            self.control = None
            
        # Atmospheric channel
        self.atm_channel = AtmosphericChannel(AtmosphericConfig(
            wavelength=self.cfg.wavelength,
            rx_aperture=self.cfg.rx_aperture,
            scintillation_index=self.cfg.scintillation_index
        ))
        
        # Thermal model
        if self.cfg.enable_thermal:
            self.thermal = VLEOThermalModel(VLEOThermalConfig())
        else:
            self.thermal = None
        
        # Tracking state
        self.tracking_error_theta = 0.0
        self.tracking_error_phi = 0.0
        self.measured_snr = 0.0
        
        # Logging
        self.log_data: List[Dict] = []
        self.last_log_time = 0.0
        
    def step(self):
        """Execute one simulation time step."""
        dt = self.cfg.dt
        
        # Propagate satellite and vehicle
        self.satellite.propagate(dt)
        self.vehicle.propagate(dt)
        
        # Get positions
        sat_pos = self.satellite.get_position_ecef()
        
        # Compute geometry
        slant_range = self.vehicle.get_slant_range_to_satellite(sat_pos)
        elevation = self.vehicle.get_elevation_angle(sat_pos)
        azimuth = self.vehicle.get_azimuth(sat_pos)
        
        # Update atmospheric channel
        self.atm_channel.update(dt, slant_range, elevation)
        
        # Update thermal model
        if self.thermal:
            # Simplified: assume sun angle changes with orbital position
            sun_angle = 45 + 45 * np.sin(self.time / self.satellite.period * 2 * np.pi)
            eclipse = sun_angle > 135
            self.thermal.update(dt, sun_angle, eclipse)
            
            # Apply thermal effects to OPA
            thermal_effects = self.thermal.get_thermal_effects_on_optics()
            # Add thermal phase drift to OPA
            # self.opa.current_phases += thermal_effects['opa_phase_drift_rad']  # Would need interface
        
        # Update OPA pointing
        if self.cfg.enable_tracking:
            if self.control:
                # Use nested control system
                measured_theta = elevation + self.atm_channel.tilt_x
                measured_phi = azimuth + self.atm_channel.tilt_y
                
                theta_cmd, phi_cmd = self.control.update(
                    measured_theta, measured_phi,
                    elevation, azimuth,
                    dt
                )
                self.opa.set_steering_angle(theta_cmd, phi_cmd)
            else:
                # Direct pointing
                self.opa.set_steering_angle(elevation, azimuth)
        
        self.opa.update(dt)
        
        # Compute optical link
        rx_power, snr = self._compute_link(
            slant_range, 
            elevation,
            self.opa.get_pointing_error()[0]
        )
        
        # Apply atmospheric channel effects
        rx_power = self.atm_channel.apply_channel(rx_power, elevation)
        
        # Process through amplifier
        if rx_power > 0:
            amp_out, amp_phase = self.amplifier.process_signal(rx_power, self.cfg.wavelength)
            self.amplifier.update_ag_dynamics(dt, amp_out / self.amplifier.cfg.effective_area)
        
        # Update tracking error estimate
        self.tracking_error_theta = self.opa.get_pointing_error()[0]
        self.measured_snr = snr
        
        # Log data
        self.time += dt
        if self.time - self.last_log_time >= self.cfg.log_interval:
            self._log_state(sat_pos, slant_range, elevation, azimuth, rx_power, snr)
            self.last_log_time = self.time
    
    def _compute_link(self, range_m: float, elevation_deg: float, 
                      pointing_error_deg: float) -> Tuple[float, float]:
        """
        Compute optical link budget.
        
        Returns:
            (rx_power_w, snr_db)
        """
        # Aperture gains
        tx_gain = self._aperture_gain(self.cfg.tx_aperture)
        rx_gain = self._aperture_gain(self.cfg.rx_aperture)
        
        # Free space path loss
        fspl_db = 20 * np.log10(4 * np.pi * range_m / self.cfg.wavelength)
        
        # Atmospheric extinction
        atm_db = self.atm_channel.compute_extinction(range_m, elevation_deg)
        
        # Pointing loss
        pointing_loss = self.cfg.pointing_loss_db + \
            12 * (pointing_error_deg / self.opa.get_beamwidth())**2
        
        # Total loss
        total_loss = fspl_db + atm_db + max(0, pointing_loss)
        
        # Received power
        tx_power_dbm = 10 * np.log10(self.cfg.tx_power * 1000)
        rx_power_dbm = tx_power_dbm + tx_gain + rx_gain - total_loss
        rx_power_w = 10**((rx_power_dbm - 30) / 10)
        
        # SNR (simplified shot-noise limited)
        responsivity = 1.0  # A/W (simplified)
        bandwidth = self.cfg.tracking_bandwidth
        q = 1.6e-19  # Electron charge
        
        if rx_power_w > 0:
            snr_linear = (responsivity * rx_power_w) / (2 * q * bandwidth)
            snr_db = 10 * np.log10(snr_linear)
        else:
            snr_db = -np.inf
            
        return max(rx_power_w, 0), snr_db
    
    def _aperture_gain(self, diameter: float) -> float:
        """Compute aperture gain [dBi]."""
        efficiency = 0.7
        gain_linear = efficiency * (np.pi * diameter / self.cfg.wavelength)**2
        return 10 * np.log10(gain_linear)
    
    def _log_state(self, sat_pos, slant_range, elevation, azimuth, rx_power, snr):
        """Log current state."""
        state = {
            'time': self.time,
            'satellite': {
                'x': sat_pos[0],
                'y': sat_pos[1],
                'z': sat_pos[2],
                'velocity': np.linalg.norm(self.satellite.get_velocity_ecef())
            },
            'vehicle': {
                'slant_range': slant_range,
                'elevation': elevation,
                'azimuth': azimuth
            },
            'optical': {
                'rx_power_dbm': 10 * np.log10(rx_power * 1000) if rx_power > 0 else -np.inf,
                'snr_db': snr,
                'pointing_error': self.tracking_error_theta,
                'beamwidth': self.opa.get_beamwidth()
            },
            'atmospheric': self.atm_channel.get_state(),
            'amplifier': self.amplifier.get_state()
        }
        
        if self.control:
            state['control'] = self.control.get_performance_metrics()
            
        if self.thermal:
            state['thermal'] = self.thermal.get_thermal_state()
        
        self.log_data.append(state)
    
    def run(self, duration: float, progress_interval: Optional[float] = None):
        """
        Run simulation for specified duration.
        
        Args:
            duration: Simulation duration [s]
            progress_interval: Print progress every N seconds [s]
        """
        n_steps = int(duration / self.cfg.dt)
        progress_steps = int(progress_interval / self.cfg.dt) if progress_interval else None
        
        print(f"Running digital twin for {duration}s ({n_steps} steps)...")
        print(f"  Subsystems: {'nested control' if self.control else 'direct'} | "
              f"{'thermal' if self.thermal else 'no thermal'} | atmospheric")
        
        for i in range(n_steps):
            self.step()
            
            if progress_steps and i % progress_steps == 0:
                progress = 100 * i / n_steps
                print(f"Progress: {progress:.1f}% | t={self.time:.3f}s | "
                      f"SNR={self.measured_snr:.1f}dB | "
                      f"Pointing_err={self.tracking_error_theta:.3f}°")
        
        print(f"Simulation complete. Logged {len(self.log_data)} data points.")
    
    def save_results(self, filepath: str):
        """Save simulation results to JSON."""
        output = {
            'config': asdict(self.cfg),
            'results': self.log_data
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"Results saved to {filepath}")
    
    def get_summary(self) -> Dict:
        """Get simulation summary statistics."""
        if not self.log_data:
            return {}
            
        snr_values = [d['optical']['snr_db'] for d in self.log_data if np.isfinite(d['optical']['snr_db'])]
        rx_values = [d['optical']['rx_power_dbm'] for d in self.log_data if np.isfinite(d['optical']['rx_power_dbm'])]
        
        summary = {
            'duration': self.time,
            'mean_snr_db': np.mean(snr_values) if snr_values else 0,
            'min_snr_db': np.min(snr_values) if snr_values else 0,
            'max_snr_db': np.max(snr_values) if snr_values else 0,
            'mean_rx_power_dbm': np.mean(rx_values) if rx_values else 0,
            'final_pointing_error': self.tracking_error_theta
        }
        
        if self.control:
            ctrl_metrics = self.control.get_performance_metrics()
            summary['control'] = ctrl_metrics
            
        return summary
