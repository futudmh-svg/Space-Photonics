"""
Ag-Doped Chalcogenide Amplifier Model

All-optical signal processing using silver-doped chalcogenide glass.
Models Kerr-based nonlinear amplification, four-wave mixing,
and all-optical switching dynamics.
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class AgChalcogenideConfig:
    """Ag-chalcogenide amplifier parameters."""
    # Material properties
    n2: float = 2.5e-18           # Nonlinear refractive index [m^2/W]
    beta_tpa: float = 0.5e-11     # Two-photon absorption [m/W]
    length: float = 1e-3          # Waveguide length [m]
    effective_area: float = 1e-12  # Mode effective area [m^2]
    
    # Gain parameters
    small_signal_gain: float = 20  # dB
    saturation_power: float = 1e-3  # Saturation power [W]
    gain_bandwidth: float = 10e12   # Bandwidth [Hz]
    
    # Silver migration dynamics
    ag_diffusion_coeff: float = 1e-15  # Diffusion coefficient [m^2/s]
    ag_ionization_time: float = 1e-6   # Photo-ionization time [s]
    
    # Thermal
    thermo_optic_coeff: float = 2e-4   # dn/dT [1/K]
    thermal_time_constant: float = 1e-3  # Thermal relaxation [s]


class AgChalcogenideAmplifier:
    """
    All-optical amplifier using Ag-doped chalcogenide.
    
    Models:
    - Kerr-based nonlinear phase shift
    - Four-wave mixing gain
    - Silver migration dynamics
    - Thermal effects
    """
    
    def __init__(self, config: AgChalcogenideConfig):
        self.cfg = config
        self.gamma = self._compute_nonlinear_coefficient()
        
        # State variables
        self.input_power = 0.0
        self.output_power = 0.0
        self.phase_shift = 0.0
        self.ag_concentration = 0.0
        self.temperature = 300.0  # K
        self.thermal_phase = 0.0
        
        # Saturation state
        self.gain_reduction = 0.0
        
    def _compute_nonlinear_coefficient(self) -> float:
        """
        Compute nonlinear parameter gamma [1/(W*m)].
        gamma = 2*pi*n2 / (lambda*Aeff)
        """
        lambda_m = 1550e-9  # Assume 1550nm
        gamma = 2 * np.pi * self.cfg.n2 / (lambda_m * self.cfg.effective_area)
        return gamma
    
    def process_signal(self, power_w: float, wavelength: float = 1550e-9) -> Tuple[float, float]:
        """
        Process optical signal through amplifier.
        
        Args:
            power_w: Input optical power [W]
            wavelength: Signal wavelength [m]
            
        Returns:
            (output_power_w, phase_shift_rad)
        """
        self.input_power = power_w
        
        # Compute gain with saturation
        g0 = 10**(self.cfg.small_signal_gain / 10)
        saturation = power_w / self.cfg.saturation_power
        gain = g0 / (1 + saturation)
        self.gain_reduction = 1 / (1 + saturation)
        
        # Output power
        self.output_power = power_w * gain
        
        # Nonlinear phase shift (Kerr effect)
        # phi_NL = gamma * L_eff * P
        l_eff = self.cfg.length  # Simplified: no loss
        self.phase_shift = self.gamma * l_eff * self.output_power
        
        # Thermal phase shift
        delta_T = self.thermo_optic_coeff * self.output_power * 0.1  # Simplified heating
        self.thermal_phase = 2 * np.pi / wavelength * self.cfg.length * delta_T
        
        total_phase = self.phase_shift + self.thermal_phase
        
        return self.output_power, total_phase
    
    def update_ag_dynamics(self, dt: float, optical_intensity: float):
        """
        Update silver migration dynamics.
        
        Args:
            dt: Time step [s]
            optical_intensity: Local optical intensity [W/m^2]
        """
        # Photo-induced silver ionization
        ionization_rate = optical_intensity / self.cfg.ag_ionization_time
        
        # Diffusion (simplified)
        diffusion = -self.cfg.ag_diffusion_coeff * self.ag_concentration
        
        # Update concentration
        self.ag_concentration += dt * (ionization_rate + diffusion)
        self.ag_concentration = np.clip(self.ag_concentration, 0, 1)
        
    def compute_fwm_gain(self, pump_power: float, signal_power: float, 
                         delta_lambda: float) -> float:
        """
        Compute four-wave mixing gain.
        
        Args:
            pump_power: Pump power [W]
            signal_power: Signal power [W]
            delta_lambda: Wavelength detuning [m]
            
        Returns:
            FWM conversion efficiency [linear]
        """
        # Phase mismatch
        beta2 = -20e-27  # GVD [s^2/m] - typical for chalcogenide
        delta_omega = 2 * np.pi * 3e8 / 1550e-9**2 * delta_lambda
        delta_beta = beta2 * delta_omega**2
        
        # FWM efficiency (simplified)
        l = self.cfg.length
        gamma_p = self.gamma * pump_power
        
        if abs(delta_beta) < 1e-20:
            efficiency = (gamma_p * l)**2
        else:
            efficiency = (gamma_p / delta_beta * np.sin(delta_beta * l / 2))**2
            
        return efficiency
    
    def get_state(self) -> dict:
        """Return current amplifier state."""
        return {
            'input_power_w': self.input_power,
            'output_power_w': self.output_power,
            'gain_db': 10 * np.log10(self.output_power / max(self.input_power, 1e-12)),
            'phase_shift_rad': self.phase_shift,
            'thermal_phase_rad': self.thermal_phase,
            'ag_concentration': self.ag_concentration,
            'temperature_k': self.temperature,
            'gamma': self.gamma,
            'gain_reduction': self.gain_reduction
        }
