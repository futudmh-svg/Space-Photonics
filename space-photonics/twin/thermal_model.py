"""
VLEO Thermal Environment Model

Models thermal effects on optical systems in very low Earth orbit:
- Atomic oxygen drag heating
- Solar radiation
- Earth albedo/IR
- Aerothermal heating
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class VLEOThermalConfig:
    """VLEO thermal environment parameters."""
    # Orbit
    altitude: float = 300e3         # Orbital altitude [m]
    
    # Thermal properties
    absorptivity: float = 0.3       # Solar absorptivity
    emissivity: float = 0.85        # IR emissivity
    
    # Satellite properties
    mass: float = 100.0             # Satellite mass [kg]
    surface_area: float = 2.0       # Exposed surface area [m^2]
    specific_heat: float = 900.0    # Specific heat [J/kg/K]
    
    # Optical payload
    optical_mass: float = 10.0      # Optical payload mass [kg]
    optical_area: float = 0.5       # Optical payload area [m^2]
    optical_thermal_mass: float = 5.0  # Thermal mass [J/K]
    
    # Heaters
    heater_power: float = 10.0      # Heater power [W]
    heater_setpoint: float = 293.0  # Setpoint [K] = 20°C


class VLEOThermalModel:
    """
    Thermal model for VLEO optical payloads.
    
    Models the dominant heating/cooling mechanisms:
    1. Aerothermal heating from atomic oxygen
    2. Solar radiation
    3. Earth IR and albedo
    4. Radiative cooling to space
    """
    
    def __init__(self, config: VLEOThermalConfig):
        self.cfg = config
        
        # Thermal state
        self.satellite_temp = 300.0     # K
        self.optical_temp = 300.0       # K
        self.heater_on = False
        
        # Derived constants
        self._compute_orbit_params()
        
    def _compute_orbit_params(self):
        """Compute orbital thermal parameters."""
        # Orbital velocity
        mu = 3.986e14  # Earth gravity [m^3/s^2]
        r = self.cfg.altitude + 6371e3
        self.orbital_velocity = np.sqrt(mu / r)
        
        # Orbital period
        self.period = 2 * np.pi * r / self.orbital_velocity
        
        # Atmospheric density (simple exponential model)
        rho0 = 1.225  # Sea level [kg/m^3]
        H = 8.5e3     # Scale height [m]
        self.atm_density = rho0 * np.exp(-self.cfg.altitude / H)
        
    def compute_aerothermal_heating(self) -> float:
        """
        Compute aerodynamic heating [W/m^2].
        
        q_dot = 0.5 * rho * v^3 * C_d
        """
        # Drag coefficient (typical for satellite)
        Cd = 2.2
        
        # Heating flux
        q_aero = 0.5 * self.atm_density * self.orbital_velocity**3 * Cd
        
        return q_aero
    
    def compute_solar_flux(self, sun_angle: float) -> float:
        """
        Compute solar heating flux [W/m^2].
        
        Args:
            sun_angle: Angle from sun vector to surface normal [deg]
        """
        S0 = 1361  # Solar constant [W/m^2]
        
        # Account for Earth's shadow (simplified)
        # Assume in sunlight if sun_angle < 90 deg
        if sun_angle > 90:
            return 0.0
            
        # Projected flux
        flux = S0 * np.cos(np.radians(sun_angle))
        
        return max(0, flux)
    
    def compute_earth_ir(self) -> float:
        """
        Compute Earth IR flux [W/m^2].
        """
        # Earth emits as blackbody at ~255K
        sigma = 5.67e-8  # Stefan-Boltzmann
        T_earth = 255.0
        
        # View factor from LEO (simplified: F ~ 0.5 for nadir-facing)
        F = 0.5
        
        q_ir = F * sigma * T_earth**4
        
        return q_ir
    
    def compute_albedo(self, sun_angle: float) -> float:
        """
        Compute Earth albedo flux [W/m^2].
        """
        # Albedo factor (~0.3 average)
        albedo = 0.3
        
        solar_flux = self.compute_solar_flux(sun_angle)
        q_albedo = albedo * solar_flux * 0.5  # View factor
        
        return q_albedo
    
    def compute_radiative_cooling(self, temp: float) -> float:
        """
        Compute radiative cooling flux [W/m^2].
        """
        sigma = 5.67e-8
        T_space = 3.0  # Space temperature [K]
        
        q_rad = self.cfg.emissivity * sigma * (temp**4 - T_space**4)
        
        return q_rad
    
    def update(self, dt: float, sun_angle: float = 45.0, 
               eclipse: bool = False):
        """
        Update thermal state.
        
        Args:
            dt: Time step [s]
            sun_angle: Sun incidence angle [deg]
            eclipse: True if in Earth's shadow
        """
        if eclipse:
            sun_angle = 180  # No direct sun
            
        # Satellite body thermal balance
        q_solar = self.compute_solar_flux(sun_angle)
        q_ir = self.compute_earth_ir()
        q_albedo = self.compute_albedo(sun_angle)
        q_aero = self.compute_aerothermal_heating()
        q_rad = self.compute_radiative_cooling(self.satellite_temp)
        
        # Net heat flux on satellite
        q_in = (q_solar * self.cfg.absorptivity + 
                q_ir + q_albedo + q_aero) * self.cfg.surface_area
        q_out = q_rad * self.cfg.surface_area
        
        # Heater control (bang-bang)
        if self.satellite_temp < self.cfg.heater_setpoint - 2:
            self.heater_on = True
        elif self.satellite_temp > self.cfg.heater_setpoint + 2:
            self.heater_on = False
            
        q_heater = self.cfg.heater_power if self.heater_on else 0
        
        # Temperature update
        dT = (q_in - q_out + q_heater) / (self.cfg.mass * self.cfg.specific_heat)
        self.satellite_temp += dT * dt
        
        # Optical payload thermal balance (coupled to satellite)
        # Optical payload has different thermal environment
        q_optical_in = (q_solar * self.cfg.absorptivity * 0.3 + 
                       q_ir * 0.5) * self.cfg.optical_area
        q_optical_rad = self.compute_radiative_cooling(self.optical_temp) * self.cfg.optical_area
        
        # Conductive coupling to satellite body
        k_contact = 10.0  # Contact conductance [W/K]
        q_conduction = k_contact * (self.satellite_temp - self.optical_temp)
        
        dT_opt = (q_optical_in - q_optical_rad + q_conduction) / self.cfg.optical_thermal_mass
        self.optical_temp += dT_opt * dt
        
    def get_thermal_state(self) -> dict:
        """Get current thermal state."""
        return {
            'satellite_temp_c': self.satellite_temp - 273.15,
            'optical_temp_c': self.optical_temp - 273.15,
            'heater_on': self.heater_on,
            'atmospheric_density': self.atm_density,
            'aerothermal_flux': self.compute_aerothermal_heating(),
            'thermal_stable': abs(self.satellite_temp - self.cfg.heater_setpoint) < 5
        }
    
    def get_thermal_effects_on_optics(self) -> dict:
        """
        Get thermal effects on optical system performance.
        
        Returns:
            dict with thermal lensing, index change, etc.
        """
        # Thermo-optic coefficient for fused silica (TFLN substrate)
        dn_dT = 1e-5  # [1/K]
        
        # Thermal lensing (simplified)
        delta_n = dn_dT * (self.optical_temp - 300)
        
        # OPA phase drift
        phase_drift = 2 * np.pi / 1550e-9 * 1e-3 * delta_n
        
        return {
            'thermooptic_index_change': delta_n,
            'opa_phase_drift_rad': phase_drift,
            'beam_defocus_m': 0.0,  # Would need lens geometry
            'resonator_detuning_hz': 0.0  # Would need cavity parameters
        }
