"""
Nested Control Loop Model

Optical inner loop (ns-timescale) + digital outer loop (μs-timescale)
for tracking hypersonic vehicles.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class OpticalLoopConfig:
    """All-optical phase-locked loop parameters."""
    bandwidth: float = 1e9          # Loop bandwidth [Hz]
    damping: float = 0.707          # Damping ratio
    detector_responsivity: float = 1.0  # A/W
    vco_gain: float = 1e9           # VCO gain [Hz/V]
    delay: float = 100e-12          # Loop delay [s]
    
    # Kerr-based phase detector
    kerr_nonlinearity: float = 2.5e-18  # m^2/W
    waveguide_length: float = 1e-3      # m


@dataclass
class DigitalLoopConfig:
    """Digital tracking loop (Kalman filter) parameters."""
    sample_rate: float = 1e6        # Sample rate [Hz]
    process_noise: float = 1.0      # Process noise covariance
    measurement_noise: float = 0.1  # Measurement noise covariance
    prediction_horizon: float = 100e-6  # Prediction horizon [s]
    
    # Tracking bandwidth
    bandwidth: float = 10e3         # Hz


class OpticalPhaseLockedLoop:
    """
    All-optical phase-locked loop using Kerr nonlinearity.
    
    Models ns-timescale phase tracking for fast beam steering.
    """
    
    def __init__(self, config: OpticalLoopConfig):
        self.cfg = config
        
        # Loop filter state (second-order PLL)
        self.phase_error = 0.0
        self.freq_error = 0.0
        self.control_voltage = 0.0
        
        # Loop filter coefficients
        self._compute_filter_coeffs()
        
        # History for delay compensation
        self.delay_buffer = []
        self.delay_samples = max(1, int(config.delay * config.bandwidth))
        
    def _compute_filter_coeffs(self):
        """Compute proportional-integral filter coefficients."""
        # Natural frequency
        omega_n = 2 * np.pi * self.cfg.bandwidth
        
        # Standard second-order loop
        # Kp = 2*zeta*omega_n / Kvco
        # Ki = omega_n^2 / Kvco
        self.kp = 2 * self.cfg.damping * omega_n / self.cfg.vco_gain
        self.ki = omega_n**2 / self.cfg.vco_gain
        
    def update(self, measured_phase: float, reference_phase: float, dt: float) -> float:
        """
        Update PLL state.
        
        Args:
            measured_phase: Detected phase [rad]
            reference_phase: Reference phase [rad]
            dt: Time step [s]
            
        Returns:
            Control voltage [V]
        """
        # Phase error
        self.phase_error = reference_phase - measured_phase
        
        # Wrap to [-pi, pi]
        self.phase_error = np.mod(self.phase_error + np.pi, 2*np.pi) - np.pi
        
        # Delay compensation
        self.delay_buffer.append(self.phase_error)
        if len(self.delay_buffer) > self.delay_samples:
            delayed_error = self.delay_buffer.pop(0)
        else:
            delayed_error = self.phase_error
        
        # Loop filter (PI)
        self.freq_error += self.ki * delayed_error * dt
        self.control_voltage = self.kp * delayed_error + self.freq_error
        
        return self.control_voltage
    
    def get_bandwidth(self) -> float:
        """Return loop bandwidth [Hz]."""
        return self.cfg.bandwidth
    
    def get_lock_status(self) -> bool:
        """Return True if PLL is locked."""
        return abs(self.phase_error) < np.pi / 4  # Within 45 deg


class DigitalKalmanTracker:
    """
    Digital Kalman filter for hypersonic vehicle tracking.
    
    Predicts vehicle trajectory and provides pointing commands
    to the OPA at μs-timescale.
    """
    
    def __init__(self, config: DigitalLoopConfig):
        self.cfg = config
        
        # State vector: [theta, dtheta/dt, d2theta/dt2, phi, dphi/dt]
        self.state = np.zeros(5)
        self.covariance = np.eye(5) * 1.0
        
        # Process model (constant acceleration)
        dt = 1.0 / config.sample_rate
        self.F = np.array([
            [1, dt, 0.5*dt**2, 0, 0],
            [0, 1, dt, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, dt],
            [0, 0, 0, 0, 1]
        ])
        
        # Process noise
        self.Q = np.eye(5) * config.process_noise
        
        # Measurement matrix (we measure theta and phi)
        self.H = np.array([
            [1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0]
        ])
        
        # Measurement noise
        self.R = np.eye(2) * config.measurement_noise
        
        # Prediction horizon for lead-ahead
        self.pred_horizon = config.prediction_horizon
        
    def predict(self):
        """State prediction step."""
        self.state = self.F @ self.state
        self.covariance = self.F @ self.covariance @ self.F.T + self.Q
        
    def update(self, measured_theta: float, measured_phi: float):
        """
        Measurement update step.
        
        Args:
            measured_theta: Measured elevation [deg]
            measured_phi: Measured azimuth [deg]
        """
        z = np.array([measured_theta, measured_phi])
        
        # Innovation
        y = z - self.H @ self.state
        
        # Innovation covariance
        S = self.H @ self.covariance @ self.H.T + self.R
        
        # Kalman gain
        K = self.covariance @ self.H.T @ np.linalg.inv(S)
        
        # State update
        self.state = self.state + K @ y
        
        # Covariance update (Joseph form for stability)
        I_KH = np.eye(5) - K @ self.H
        self.covariance = I_KH @ self.covariance @ I_KH.T + K @ self.R @ K.T
        
    def get_pointing_command(self) -> Tuple[float, float]:
        """
        Get predicted pointing angles with lead-ahead.
        
        Returns:
            (theta_cmd, phi_cmd) in degrees
        """
        # Predict forward by horizon time
        dt = self.pred_horizon
        theta_pred = self.state[0] + self.state[1]*dt + 0.5*self.state[2]*dt**2
        phi_pred = self.state[3] + self.state[4]*dt
        
        return theta_pred, phi_pred
    
    def get_state_uncertainty(self) -> Tuple[float, float]:
        """
        Get state uncertainty (1-sigma).
        
        Returns:
            (theta_sigma, phi_sigma) in degrees
        """
        theta_sigma = np.sqrt(self.covariance[0, 0])
        phi_sigma = np.sqrt(self.covariance[3, 3])
        return theta_sigma, phi_sigma


class NestedControlSystem:
    """
    Complete nested control system.
    
    Outer: Digital Kalman filter (μs)
    Inner: Optical PLL (ns)
    """
    
    def __init__(self, optical_config: Optional[OpticalLoopConfig] = None,
                 digital_config: Optional[DigitalLoopConfig] = None):
        self.optical_loop = OpticalPhaseLockedLoop(optical_config or OpticalLoopConfig())
        self.digital_tracker = DigitalKalmanTracker(digital_config or DigitalLoopConfig())
        
        # Tracking metrics
        self.total_pointing_error = 0.0
        self.rms_error = 0.0
        self.error_history = []
        
    def update(self, measured_theta: float, measured_phi: float,
               target_theta: float, target_phi: float,
               dt: float) -> Tuple[float, float]:
        """
        Update both control loops.
        
        Args:
            measured_theta: Measured elevation [deg]
            measured_phi: Measured azimuth [deg]
            target_theta: Target elevation [deg]
            target_phi: Target azimuth [deg]
            dt: Time step [s]
            
        Returns:
            (corrected_theta, corrected_phi) pointing commands [deg]
        """
        # Outer loop: Digital Kalman filter
        self.digital_tracker.predict()
        self.digital_tracker.update(measured_theta, measured_phi)
        
        # Get predicted pointing with lead-ahead
        theta_cmd, phi_cmd = self.digital_tracker.get_pointing_command()
        
        # Inner loop: Optical PLL for fine phase correction
        # Convert angle error to phase error
        angle_error = target_theta - theta_cmd
        phase_error = np.radians(angle_error)  # Simplified
        
        vco_out = self.optical_loop.update(phase_error, 0.0, dt)
        
        # Apply correction
        corrected_theta = theta_cmd + np.degrees(vco_out / self.optical_loop.cfg.vco_gain)
        corrected_phi = phi_cmd
        
        # Track error
        self.total_pointing_error = abs(target_theta - corrected_theta)
        self.error_history.append(self.total_pointing_error)
        
        return corrected_theta, corrected_phi
    
    def get_performance_metrics(self) -> dict:
        """Get tracking performance metrics."""
        if not self.error_history:
            return {}
            
        errors = np.array(self.error_history)
        return {
            'rms_pointing_error_deg': np.sqrt(np.mean(errors**2)),
            'max_pointing_error_deg': np.max(errors),
            'mean_pointing_error_deg': np.mean(errors),
            'optical_pll_locked': self.optical_loop.get_lock_status(),
            'kalman_theta_sigma': self.digital_tracker.get_state_uncertainty()[0],
            'kalman_phi_sigma': self.digital_tracker.get_state_uncertainty()[1]
        }
