"""
OPA Beam Steering Model

Multi-face optical phased array with TFLN phase shifters.
Models beam steering, side lobe suppression, and pointing errors.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class OPAConfig:
    """OPA configuration parameters."""
    num_elements: int = 64          # Number of phase shifters per axis
    pitch: float = 10e-6            # Element spacing [m]
    wavelength: float = 1550e-9     # Operating wavelength [m]
    max_steering_angle: float = 30  # Max steering angle [deg]
    phase_resolution: float = 2*np.pi / 256  # 8-bit phase control
    response_time: float = 1e-9     # TFLN phase shifter response [s]
    insertion_loss: float = 3.0     # dB
    

class OPABeamSteerer:
    """
    Multi-face OPA beam steering model.
    
    Simulates far-field pattern with phase quantization,
    thermal drift, and pointing jitter.
    """
    
    def __init__(self, config: OPAConfig):
        self.cfg = config
        self.k = 2 * np.pi / config.wavelength
        self.element_positions = np.arange(config.num_elements) * config.pitch
        
        # Phase state
        self.current_phases = np.zeros(config.num_elements)
        self.target_phases = np.zeros(config.num_elements)
        self.thermal_drift = np.zeros(config.num_elements)
        
        # Pointing state
        self.current_theta = 0.0  # Current steering angle [rad]
        self.current_phi = 0.0    # Azimuth [rad]
        
    def set_steering_angle(self, theta_deg: float, phi_deg: float = 0.0):
        """
        Set target steering angle.
        
        Args:
            theta_deg: Elevation angle from boresight [deg]
            phi_deg: Azimuth angle [deg]
        """
        theta = np.radians(np.clip(theta_deg, -self.cfg.max_steering_angle, 
                                    self.cfg.max_steering_angle))
        phi = np.radians(phi_deg)
        
        self.target_phases = -self.k * self.element_positions * np.sin(theta)
        self.current_theta = theta
        self.current_phi = phi
        
    def update(self, dt: float):
        """
        Update phase state (first-order RC response).
        
        Args:
            dt: Time step [s]
        """
        tau = self.cfg.response_time
        alpha = 1 - np.exp(-dt / tau) if tau > 0 else 1.0
        
        # Quantize target phases
        quantized_target = np.round(self.target_phases / self.cfg.phase_resolution) * self.cfg.phase_resolution
        
        # Apply thermal drift (modeled as slow random walk)
        thermal_noise = np.random.normal(0, 0.01 * self.cfg.phase_resolution, self.cfg.num_elements)
        self.thermal_drift += thermal_noise
        self.thermal_drift *= 0.999  # Slow decay
        
        # Update current phases toward target
        self.current_phases += alpha * (quantized_target - self.current_phases)
        self.current_phases += thermal_noise
        
    def compute_farfield(self, theta_range: np.ndarray, phi: float = 0.0) -> np.ndarray:
        """
        Compute far-field intensity pattern.
        
        Args:
            theta_range: Array of angles [rad]
            phi: Fixed azimuth [rad]
            
        Returns:
            Normalized intensity pattern [linear]
        """
        # Array factor
        phases = self.current_phases
        k = self.k
        d = self.cfg.pitch
        
        # Steering phase delay
        steering_phase = k * d * np.sin(self.current_theta)
        
        # Array factor
        n = np.arange(self.cfg.num_elements)
        AF = np.zeros_like(theta_range, dtype=complex)
        
        for i, th in enumerate(theta_range):
            element_phases = phases - k * d * n * np.sin(th)
            AF[i] = np.sum(np.exp(1j * element_phases))
            
        intensity = np.abs(AF)**2
        intensity /= np.max(intensity)  # Normalize
        
        # Apply insertion loss
        intensity *= 10**(-self.cfg.insertion_loss / 10)
        
        return intensity
    
    def get_pointing_error(self) -> Tuple[float, float]:
        """
        Estimate pointing error based on phase quantization and thermal drift.
        
        Returns:
            (theta_error, phi_error) in degrees
        """
        phase_rms = np.std(self.current_phases - self.target_phases)
        
        # Approximate pointing error from phase RMS
        # For small errors: d(theta) ≈ lambda / (2*pi*d*N) * d(phi_rms)
        N = self.cfg.num_elements
        d = self.cfg.pitch
        lambda_m = self.cfg.wavelength
        
        theta_error_rad = phase_rms * lambda_m / (2 * np.pi * d * N)
        theta_error_deg = np.degrees(theta_error_rad)
        
        return theta_error_deg, 0.0  # Simplified: no phi error in 1D model
    
    def get_beamwidth(self) -> float:
        """
        Estimate 3dB beamwidth [deg].
        """
        N = self.cfg.num_elements
        d = self.cfg.pitch
        lambda_m = self.cfg.wavelength
        
        # Approximate beamwidth for uniform array
        bw_rad = 0.886 * lambda_m / (N * d)
        return np.degrees(bw_rad)
