"""
Hardware-in-the-Loop Interface Stub

Provides interfaces for connecting the digital twin to
real hardware for validation and testing.
"""

import numpy as np
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class HILConfig:
    """Hardware-in-the-loop configuration."""
    update_rate: float = 1000.0     # Update rate [Hz]
    sensor_noise: float = 0.01      # Sensor noise [deg]
    actuator_delay: float = 1e-6    # Actuator delay [s]
    communication_latency: float = 1e-3  # Network latency [s]


class HILInterface:
    """
    Hardware-in-the-loop interface.
    
    Connects digital twin to real hardware:
    - OPA phase shifter controller
    - Optical power meter
    - Position sensors
    - Tracking camera
    """
    
    def __init__(self, config: HILConfig):
        self.cfg = config
        self.running = False
        
        # Sensor callbacks
        self._phase_callback: Optional[Callable] = None
        self._power_callback: Optional[Callable] = None
        self._position_callback: Optional[Callable] = None
        
        # Actuator callbacks
        self._steering_callback: Optional[Callable] = None
        self._amplifier_callback: Optional[Callable] = None
        
        # Data buffers
        self.sensor_data = []
        self.actuator_commands = []
        
    def register_phase_sensor(self, callback: Callable):
        """Register callback for phase sensor readings."""
        self._phase_callback = callback
        
    def register_power_sensor(self, callback: Callable):
        """Register callback for optical power meter."""
        self._power_callback = callback
        
    def register_position_sensor(self, callback: Callable):
        """Register callback for position sensor."""
        self._position_callback = callback
        
    def register_steering_actuator(self, callback: Callable):
        """Register callback for OPA steering actuator."""
        self._steering_callback = callback
        
    def register_amplifier_actuator(self, callback: Callable):
        """Register callback for amplifier control."""
        self._amplifier_callback = callback
        
    def read_sensors(self) -> dict:
        """
        Read all sensors with noise and latency.
        
        Returns:
            dict with sensor readings
        """
        readings = {}
        
        if self._phase_callback:
            phase = self._phase_callback()
            phase += np.random.normal(0, self.cfg.sensor_noise)
            readings['phase'] = phase
            
        if self._power_callback:
            power = self._power_callback()
            power *= (1 + np.random.normal(0, 0.02))  # 2% noise
            readings['power'] = power
            
        if self._position_callback:
            pos = self._position_callback()
            pos += np.random.normal(0, self.cfg.sensor_noise)
            readings['position'] = pos
            
        self.sensor_data.append(readings)
        return readings
    
    def write_actuators(self, steering_angle: float, amplifier_gain: float):
        """
        Write commands to actuators with delay.
        
        Args:
            steering_angle: Target steering angle [deg]
            amplifier_gain: Amplifier gain [dB]
        """
        command = {
            'steering': steering_angle,
            'gain': amplifier_gain,
            'timestamp': len(self.actuator_commands) / self.cfg.update_rate
        }
        
        if self._steering_callback:
            self._steering_callback(steering_angle)
            
        if self._amplifier_callback:
            self._amplifier_callback(amplifier_gain)
            
        self.actuator_commands.append(command)
        
    def start(self):
        """Start HIL loop."""
        self.running = True
        print("HIL interface started")
        
    def stop(self):
        """Stop HIL loop."""
        self.running = False
        print("HIL interface stopped")
        
    def get_latency_stats(self) -> dict:
        """Get communication latency statistics."""
        if not self.sensor_data or not self.actuator_commands:
            return {}
            
        return {
            'sensor_samples': len(self.sensor_data),
            'actuator_commands': len(self.actuator_commands),
            'configured_latency': self.cfg.communication_latency
        }


# Example hardware stubs
def example_phase_sensor() -> float:
    """Stub: returns phase in degrees."""
    return 0.0


def example_power_sensor() -> float:
    """Stub: returns power in mW."""
    return 1.0


def example_position_sensor() -> tuple:
    """Stub: returns (theta, phi) in degrees."""
    return (0.0, 0.0)


def example_steering_actuator(angle: float):
    """Stub: sets steering angle."""
    pass


def example_amplifier_actuator(gain: float):
    """Stub: sets amplifier gain."""
    pass


if __name__ == "__main__":
    # Demo HIL interface
    hil = HILInterface(HILConfig())
    
    # Register stubs
    hil.register_phase_sensor(example_phase_sensor)
    hil.register_power_sensor(example_power_sensor)
    hil.register_position_sensor(example_position_sensor)
    hil.register_steering_actuator(example_steering_actuator)
    hil.register_amplifier_actuator(example_amplifier_actuator)
    
    # Run for 100 cycles
    hil.start()
    for i in range(100):
        sensors = hil.read_sensors()
        hil.write_actuators(steering_angle=i*0.1, amplifier_gain=20.0)
    hil.stop()
    
    print(f"\nHIL Stats: {hil.get_latency_stats()}")
