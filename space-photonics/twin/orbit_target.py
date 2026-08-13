"""
VLEO Orbit + Hypersonic Vehicle Propagator

Simulates satellite orbital dynamics and hypersonic vehicle trajectories
for link budget and pointing calculations.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass  
class OrbitConfig:
    """VLEO orbit parameters."""
    altitude: float = 300e3         # Orbital altitude [m]
    inclination: float = 45.0       # Inclination [deg]
    eccentricity: float = 0.0       # Circular orbit
    raan: float = 0.0              # Right ascension of ascending node [deg]
    arg_perigee: float = 0.0        # Argument of perigee [deg]
    
    # Earth parameters
    mu: float = 3.986e14           # Earth's gravitational parameter [m^3/s^2]
    earth_radius: float = 6371e3    # Earth radius [m]
    

@dataclass
class VehicleConfig:
    """Hypersonic vehicle parameters."""
    altitude: float = 30e3          # Flight altitude [m]
    velocity: float = 1700          # Velocity [m/s] ~ Mach 5
    heading: float = 90.0           # Heading angle [deg] from North
    climb_rate: float = 0.0         # Vertical velocity [m/s]
    
    # Position (initial)
    lat0: float = 0.0
    lon0: float = 0.0


class VLEOPropagator:
    """VLEO satellite orbit propagator (simplified two-body)."""
    
    def __init__(self, config: OrbitConfig):
        self.cfg = config
        self.r_earth = config.earth_radius
        self.r_orbit = self.r_earth + config.altitude
        
        # Orbital period
        self.period = 2 * np.pi * np.sqrt(self.r_orbit**3 / config.mu)
        self.orbital_rate = 2 * np.pi / self.period
        
        # Current state
        self.true_anomaly = 0.0  # [rad]
        self.time = 0.0
        
    def propagate(self, dt: float):
        """Propagate orbit by time step dt [s]."""
        self.time += dt
        self.true_anomaly += self.orbital_rate * dt
        self.true_anomaly = self.true_anomaly % (2 * np.pi)
        
    def get_position_ecef(self) -> Tuple[float, float, float]:
        """
        Get satellite position in ECEF coordinates [m].
        
        Returns:
            (x, y, z) in ECEF [m]
        """
        i = np.radians(self.cfg.inclination)
        
        # Simple circular orbit in orbital plane
        x_orb = self.r_orbit * np.cos(self.true_anomaly)
        y_orb = self.r_orbit * np.sin(self.true_anomaly)
        z_orb = 0.0
        
        # Rotate by inclination (simplified - assumes RAAN=0)
        x = x_orb
        y = y_orb * np.cos(i)
        z = y_orb * np.sin(i)
        
        return x, y, z
    
    def get_velocity_ecef(self) -> Tuple[float, float, float]:
        """Get satellite velocity in ECEF [m/s]."""
        v_orbital = np.sqrt(self.cfg.mu / self.r_orbit)
        
        i = np.radians(self.cfg.inclination)
        
        vx = -v_orbital * np.sin(self.true_anomaly)
        vy = v_orbital * np.cos(self.true_anomaly) * np.cos(i)
        vz = v_orbital * np.cos(self.true_anomaly) * np.sin(i)
        
        return vx, vy, vz


class HypersonicVehicle:
    """Hypersonic vehicle trajectory model."""
    
    def __init__(self, config: VehicleConfig):
        self.cfg = config
        self.position = np.array([config.lon0, config.lat0, config.altitude])
        self.velocity = np.array([
            config.velocity * np.sin(np.radians(config.heading)),
            config.velocity * np.cos(np.radians(config.heading)),
            config.climb_rate
        ])
        self.time = 0.0
        
    def propagate(self, dt: float):
        """Propagate vehicle by time step dt [s]."""
        self.time += dt
        
        # Simple constant velocity model
        # In reality, would include aerodynamics, gravity, etc.
        self.position += self.velocity * dt
        
        # Update altitude (if climbing/diving)
        self.position[2] += self.cfg.climb_rate * dt
        self.position[2] = max(self.position[2], 0)  # Don't go below ground
        
    def get_position_ecef(self) -> Tuple[float, float, float]:
        """
        Get vehicle position in ECEF [m].
        
        Simplified: assumes flat Earth for local coordinates.
        """
        # Convert lat/lon/alt to approximate ECEF
        lat_rad = np.radians(self.position[1])
        lon_rad = np.radians(self.position[0])
        alt = self.position[2]
        
        r = self.cfg.altitude + alt  # Simplified
        
        x = r * np.cos(lat_rad) * np.cos(lon_rad)
        y = r * np.cos(lat_rad) * np.sin(lon_rad)
        z = r * np.sin(lat_rad)
        
        return x, y, z
    
    def get_slant_range_to_satellite(self, sat_pos: Tuple[float, float, float]) -> float:
        """Compute slant range to satellite [m]."""
        veh_pos = self.get_position_ecef()
        dx = sat_pos[0] - veh_pos[0]
        dy = sat_pos[1] - veh_pos[1]
        dz = sat_pos[2] - veh_pos[2]
        return np.sqrt(dx**2 + dy**2 + dz**2)
    
    def get_elevation_angle(self, sat_pos: Tuple[float, float, float]) -> float:
        """Compute elevation angle to satellite [deg]."""
        veh_pos = np.array(self.get_position_ecef())
        sat_pos = np.array(sat_pos)
        
        # Local up direction
        r_veh = np.linalg.norm(veh_pos)
        up = veh_pos / r_veh
        
        # Vector to satellite
        to_sat = sat_pos - veh_pos
        range_m = np.linalg.norm(to_sat)
        to_sat = to_sat / range_m
        
        # Elevation angle
        sin_el = np.dot(to_sat, up)
        el = np.degrees(np.arcsin(np.clip(sin_el, -1, 1)))
        
        return el
    
    def get_azimuth(self, sat_pos: Tuple[float, float, float]) -> float:
        """Compute azimuth angle to satellite [deg]."""
        # Simplified azimuth calculation
        veh_pos = np.array(self.get_position_ecef())
        sat_pos = np.array(sat_pos)
        
        dx = sat_pos[0] - veh_pos[0]
        dy = sat_pos[1] - veh_pos[1]
        
        az = np.degrees(np.arctan2(dx, dy))
        return az % 360
