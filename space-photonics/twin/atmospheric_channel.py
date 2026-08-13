"""
Atmospheric Optical Channel Model

Models turbulence, scintillation, and beam wander for
VLEO-to-hypersonic optical links.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class AtmosphericConfig:
    """Atmospheric channel parameters."""
    # Turbulence (Hufnagel-Valley model)
    cn2_ground: float = 1e-14       # Ground refractive index structure constant [m^(-2/3)]
    cn2_high_altitude: float = 1e-17  # High altitude Cn^2
    wind_speed: float = 10.0        # Wind speed [m/s]
    
    # Scintillation
    scintillation_index: float = 0.1  # Log-amplitude variance
    
    # Wavelength
    wavelength: float = 1550e-9     # [m]
    
    # Aperture averaging
    rx_aperture: float = 0.05       # Receiver aperture [m]
    
    # Extinction
    visibility_km: float = 10.0     # Meteorological visibility [km]
    

class AtmosphericChannel:
    """
    Atmospheric optical channel model.
    
    Implements:
    - Log-normal scintillation
    - Tilt/angle-of-arrival fluctuations
    - Beam wander
    - Aperture averaging
    - Atmospheric extinction
    """
    
    def __init__(self, config: AtmosphericConfig):
        self.cfg = config
        self.k = 2 * np.pi / config.wavelength
        
        # Turbulence state
        self.tilt_x = 0.0
        self.tilt_y = 0.0
        self.scintillation = 1.0
        
        # Time constants
        self.tilt_correlation_time = 1e-3  # ms
        self.scint_correlation_time = 1e-2  # 10ms
        
    def compute_r0(self, elevation_deg: float) -> float:
        """
        Compute Fried parameter r0 [m].
        
        Args:
            elevation_deg: Elevation angle [deg]
            
        Returns:
            Fried parameter r0 [m]
        """
        # Simplified model: r0 ~ lambda^(6/5) * (cos(elevation))^(3/5) / Cn2_integral^(3/5)
        # For VLEO, path is short but Cn^2 can be high at low elevations
        
        elevation_rad = np.radians(max(elevation_deg, 5))
        
        # Hufnagel-Valley simplified integral
        # For slant path through troposphere
        cn2_integral = self.cfg.cn2_ground * 1e3 / np.sin(elevation_rad)  # Simplified
        
        r0 = (0.423 * self.k**2 * cn2_integral)**(-3/5)
        
        return r0
    
    def compute_tilt_variance(self, elevation_deg: float, 
                              aperture_diameter: float) -> float:
        """
        Compute tilt variance [rad^2].
        
        Args:
            elevation_deg: Elevation angle [deg]
            aperture_diameter: Aperture diameter [m]
            
        Returns:
            Tilt variance [rad^2]
        """
        r0 = self.compute_r0(elevation_deg)
        
        # Tilt variance for Kolmogorov turbulence
        # sigma_tilt^2 ~ (D/r0)^(-1/3) * (lambda/D)^2
        if r0 > 0 and aperture_diameter > 0:
            variance = 0.182 * (aperture_diameter / r0)**(-1/3) * \
                      (self.cfg.wavelength / aperture_diameter)**2
        else:
            variance = 0.0
            
        return variance
    
    def compute_scintillation_index(self, slant_range: float, 
                                    elevation_deg: float) -> float:
        """
        Compute scintillation index (sigma_I^2 / <I>^2).
        
        Args:
            slant_range: Slant range [m]
            elevation_deg: Elevation angle [deg]
            
        Returns:
            Scintillation index [unitless]
        """
        # Rytov variance for plane wave
        # sigma_I^2 = 1.23 * Cn2 * k^(7/6) * L^(11/6)
        
        cn2 = self.cfg.cn2_ground
        L = slant_range
        
        rytov_var = 1.23 * cn2 * self.k**(7/6) * L**(11/6)
        
        # Aperture averaging reduction
        r0 = self.compute_r0(elevation_deg)
        D = self.cfg.rx_aperture
        
        if D > 0 and r0 > 0:
            # Aperture averaging factor for plane wave
            A = np.pi * D**2 / 4
            # Simplified: reduce scintillation by aperture averaging
            aperture_factor = min(1.0, (r0 / D)**2)
            scint_index = rytov_var * aperture_factor
        else:
            scint_index = rytov_var
            
        # Saturation: scintillation index < 1 for strong turbulence
        return min(scint_index, 1.0)
    
    def compute_extinction(self, slant_range: float, 
                          elevation_deg: float) -> float:
        """
        Compute atmospheric extinction in dB.
        
        Args:
            slant_range: Slant range [m]
            elevation_deg: Elevation angle [deg]
            
        Returns:
            Extinction [dB]
        """
        # Visibility-based extinction coefficient
        # alpha = 3.91 / V * (lambda / 550nm)^(-q)
        # q = 1.3 for V < 6km, q = 1.6 for V > 50km, q = 1.3 for intermediate
        
        V = self.cfg.visibility_km * 1000  # Convert to m
        
        if V < 6e3:
            q = 1.3
        elif V > 50e3:
            q = 1.6
        else:
            q = 1.3  # Simplified
            
        alpha = 3.91 / V * (self.cfg.wavelength / 550e-9)**(-q)
        
        # Path length
        path_length = slant_range / np.sin(np.radians(max(elevation_deg, 5)))
        
        # Extinction in dB
        tau = alpha * path_length
        extinction_db = 4.343 * tau
        
        return extinction_db
    
    def update(self, dt: float, slant_range: float, elevation_deg: float):
        """
        Update atmospheric channel state.
        
        Args:
            dt: Time step [s]
            slant_range: Current slant range [m]
            elevation_deg: Elevation angle [deg]
        """
        # Update tilt (Ornstein-Uhlenbeck process)
        tilt_var = self.compute_tilt_variance(elevation_deg, self.cfg.rx_aperture)
        tilt_sigma = np.sqrt(tilt_var)
        
        alpha_tilt = 1 - np.exp(-dt / self.tilt_correlation_time)
        noise_tilt = np.random.normal(0, tilt_sigma)
        
        self.tilt_x += alpha_tilt * (noise_tilt - self.tilt_x)
        self.tilt_y += alpha_tilt * (noise_tilt - self.tilt_y)
        
        # Update scintillation (log-normal)
        sci_index = self.compute_scintillation_index(slant_range, elevation_deg)
        
        alpha_sci = 1 - np.exp(-dt / self.scint_correlation_time)
        # Log-normal: I = exp(2*chi), where chi ~ N(0, sigma_chi^2)
        # sigma_I^2 = <I>^2 * (exp(4*sigma_chi^2) - 1)
        # For weak scintillation: sigma_chi^2 ~ sigma_I^2 / 4
        sigma_chi = np.sqrt(sci_index / 4)
        chi = np.random.normal(0, sigma_chi)
        
        self.scintillation += alpha_sci * (np.exp(2*chi) - self.scintillation)
        self.scintillation = np.clip(self.scintillation, 0.01, 10.0)
        
    def apply_channel(self, power_w: float, elevation_deg: float) -> float:
        """
        Apply atmospheric channel effects to optical signal.
        
        Args:
            power_w: Input optical power [W]
            elevation_deg: Elevation angle [deg]
            
        Returns:
            Power after channel effects [W]
        """
        # Apply scintillation (fading)
        faded_power = power_w * self.scintillation
        
        # Apply tilt loss (approximate)
        tilt_var = self.compute_tilt_variance(elevation_deg, self.cfg.rx_aperture)
        tilt_loss = np.exp(-2 * tilt_var / (self.cfg.wavelength / self.cfg.rx_aperture)**2)
        
        return faded_power * tilt_loss
    
    def get_state(self) -> dict:
        """Get current channel state."""
        return {
            'tilt_x': self.tilt_x,
            'tilt_y': self.tilt_y,
            'scintillation': self.scintillation,
            'r0': 0.0,  # Computed on demand
            'turbulence_strength': 'weak' if self.scintillation < 0.3 else \
                                  ('moderate' if self.scintillation < 1.0 else 'strong')
        }
