"""
BTO (Barium Titanate) Phase Shifter Model

Alternative to TFLN phase shifters for OPA beam steering.
BTO offers ~30x higher electro-optic coefficient than lithium niobate,
enabling lower drive voltage and faster switching.

Key advantages over TFLN:
- Electro-optic coefficient: r_eff ~ 900 pm/V (vs ~30 pm/V for TFLN)
- Vπ·L product: < 0.1 V·cm (vs ~2 V·cm for TFLN)
- Switching speed: < 100 ps (electro-optic, no thermal tuning)
- No thermal crosstalk between phase shifters
- Lower power consumption per phase shift

Trade-offs:
- Much less mature technology (no commercial PDK as of 2026)
- Integration with silicon/TFLN platforms still research-grade
- Ferroelectric domain switching can cause hysteresis
- Film quality and uniformity challenges
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class BTOPhaseShifterConfig:
    """BTO phase shifter configuration."""
    # Electro-optic properties
    r_eff: float = 300e-12           # Effective EO coefficient [m/V] (thin film)
    n0: float = 2.4                  # Base refractive index
    
    # Waveguide geometry
    length: float = 100e-6           # Phase shifter length [m]
    width: float = 1e-6              # Waveguide width [m]
    height: float = 0.5e-6           # BTO film thickness [m]
    gap: float = 2e-6                # Electrode gap [m]
    
    # Electrical
    electrode_resistance: float = 50   # Electrode resistance [Ohm]
    capacitance: float = 10e-15       # Capacitance [F]
    max_voltage: float = 5.0          # Max drive voltage [V]
    
    # Switching dynamics
    switching_time: float = 50e-12    # Switching time [s]
    hysteresis: float = 0.05          # Hysteresis factor [0-1]
    
    # Thermal (minimal compared to TFLN)
    thermo_optic_coeff: float = 2e-4  # dn/dT [1/K]
    thermal_time_constant: float = 1e-6  # Fast thermal relaxation [s]
    
    # Material losses
    propagation_loss_db_cm: float = 2.0  # [dB/cm]


class BTOPhaseShifter:
    """
    Barium Titanate (BTO) phase shifter for OPA applications.
    
    Models:
    - Electro-optic phase shift (Pockels effect)
    - Fast switching dynamics
    - Ferroelectric hysteresis
    - Minimal thermal effects
    """
    
    def __init__(self, config: BTOPhaseShifterConfig):
        self.cfg = config
        
        # State
        self.voltage = 0.0
        self.target_voltage = 0.0
        self.phase_shift = 0.0
        self.temperature = 300.0  # K
        self.thermal_phase = 0.0
        self.prev_voltage = 0.0  # For hysteresis
        
        # Precompute Vπ
        self.v_pi = self._compute_v_pi()
        
    def _compute_v_pi(self) -> float:
        """Compute Vπ voltage for π phase shift."""
        # Δn = 0.5 * n0^3 * r_eff * E
        # E = V / gap
        # For π phase shift: Δn * (2π/λ) * L = π
        # => Δn = λ / (2L)
        # => Vπ = λ * gap / (n0^3 * r_eff * L)
        # Using 1550 nm as reference:
        wavelength = 1550e-9
        v_pi = wavelength * self.cfg.gap / (
            self.cfg.n0**3 * self.cfg.r_eff * self.cfg.length
        )
        return v_pi
    
    def set_voltage(self, voltage: float):
        """Set target voltage."""
        self.target_voltage = np.clip(voltage, -self.cfg.max_voltage, 
                                      self.cfg.max_voltage)
    
    def set_phase(self, phase: float, wavelength: float = 1550e-9):
        """
        Set desired phase shift and compute required voltage.
        
        Args:
            phase: Target phase shift [rad]
            wavelength: Operating wavelength [m]
        """
        # V = Vπ * (phase / π)
        voltage = self.v_pi * (phase / np.pi)
        self.set_voltage(voltage)
    
    def step(self, dt: float):
        """
        Update phase shifter state.
        
        Args:
            dt: Time step [s]
        """
        # Voltage settling (RC limited)
        rc_time = self.cfg.electrode_resistance * self.cfg.capacitance
        if rc_time > 0:
            alpha = 1 - np.exp(-dt / rc_time)
        else:
            alpha = 1.0
        self.voltage += alpha * (self.target_voltage - self.voltage)
        
        # Hysteresis model (ferroelectric domain switching)
        voltage_diff = self.voltage - self.prev_voltage
        hysteresis_offset = self.cfg.hysteresis * voltage_diff * 0.1
        effective_voltage = self.voltage - hysteresis_offset
        self.prev_voltage = self.voltage
        
        # Electro-optic phase shift
        # Δn = 0.5 * n0^3 * r_eff * (V / gap)
        delta_n = 0.5 * self.cfg.n0**3 * self.cfg.r_eff * (effective_voltage / self.cfg.gap)
        eo_phase = (2 * np.pi / 1550e-9) * delta_n * self.cfg.length
        
        # Minimal thermal phase (BTO is primarily EO, not thermo-optic)
        # Just a small residual effect
        self.thermal_phase *= np.exp(-dt / self.cfg.thermal_time_constant)
        
        self.phase_shift = eo_phase + self.thermal_phase
        
    def get_insertion_loss_db(self) -> float:
        """Get insertion loss [dB]."""
        return self.cfg.propagation_loss_db_cm * (self.cfg.length * 100)
    
    def get_power_consumption(self) -> float:
        """Get power consumption [W]."""
        # P = V^2 / R
        return self.voltage**2 / self.cfg.electrode_resistance
    
    def reset(self):
        """Reset to initial state."""
        self.voltage = 0.0
        self.target_voltage = 0.0
        self.phase_shift = 0.0
        self.thermal_phase = 0.0
        self.prev_voltage = 0.0


@dataclass
class BTOOPAConfig:
    """BTO-based OPA configuration."""
    wavelength: float = 1550e-9
    num_elements: int = 64
    element_spacing: float = 10e-6
    num_faces: int = 4
    
    # BTO phase shifter parameters
    phase_shifter_config: BTOPhaseShifterConfig = None
    
    def __post_init__(self):
        if self.phase_shifter_config is None:
            self.phase_shifter_config = BTOPhaseShifterConfig()


class BTOOPA:
    """
    BTO-based Optical Phased Array.
    
    Drop-in replacement for TFLN-based OPA with much lower
    drive voltage requirements.
    """
    
    def __init__(self, config: BTOOPAConfig):
        self.cfg = config
        
        # Create phase shifter array
        self.phase_shifters = [
            BTOPhaseShifter(self.cfg.phase_shifter_config)
            for _ in range(self.cfg.num_elements)
        ]
        
        # Steering state
        self.steering_theta = 0.0
        self.steering_phi = 0.0
        
    def set_steering_angle(self, theta: float, phi: float = 0.0):
        """
        Set steering angle and compute phase delays.
        
        Args:
            theta: Azimuth angle [deg]
            phi: Elevation angle [deg]
        """
        self.steering_theta = theta
        self.steering_phi = phi
        
        theta_rad = np.radians(theta)
        phi_rad = np.radians(phi)
        
        k = 2 * np.pi / self.cfg.wavelength
        d = self.cfg.element_spacing
        
        # Phase delay per element
        for i, ps in enumerate(self.phase_shifters):
            phase = -k * d * i * np.sin(theta_rad) * np.cos(phi_rad)
            ps.set_phase(phase, self.cfg.wavelength)
    
    def step(self, dt: float):
        """Update all phase shifters."""
        for ps in self.phase_shifters:
            ps.step(dt)
    
    def compute_farfield(self, theta: np.ndarray, phi: float = 0.0) -> np.ndarray:
        """
        Compute far-field intensity pattern.
        
        Args:
            theta: Array of angles [rad]
            phi: Elevation angle [rad]
            
        Returns:
            Normalized intensity array
        """
        k = 2 * np.pi / self.cfg.wavelength
        d = self.cfg.element_spacing
        N = self.cfg.num_elements
        
        # Get actual phase shifts
        phases = np.array([ps.phase_shift for ps in self.phase_shifters])
        
        # Array factor
        theta = np.atleast_1d(theta)
        intensity = np.zeros_like(theta)
        
        for i, th in enumerate(theta):
            phase_progression = k * d * np.arange(N) * np.sin(th) * np.cos(phi)
            total_phase = phase_progression + phases
            field = np.sum(np.exp(1j * total_phase))
            intensity[i] = np.abs(field)**2
        
        return intensity / (N**2)
    
    def get_total_power_consumption(self) -> float:
        """Get total power consumption [W]."""
        return sum(ps.get_power_consumption() for ps in self.phase_shifters)
    
    def get_total_insertion_loss_db(self) -> float:
        """Get total insertion loss [dB]."""
        return sum(ps.get_insertion_loss_db() for ps in self.phase_shifters)
    
    def reset(self):
        """Reset all phase shifters."""
        for ps in self.phase_shifters:
            ps.reset()


def compare_tfln_vs_bto():
    """Compare TFLN and BTO phase shifter performance."""
    try:
        from .opa_beamsteer import OPABeamSteerer, OPAConfig
    except ImportError:
        from opa_beamsteer import OPABeamSteerer, OPAConfig
    
    print("=" * 70)
    print("TFLN vs BTO Phase Shifter Comparison")
    print("=" * 70)
    
    # TFLN phase shifter (from existing model)
    tfln_opa = OPABeamSteerer(OPAConfig(wavelength=1550e-9, num_elements=64))
    tfln_opa.set_steering_angle(15.0)
    
    # BTO phase shifter
    bto_opa = BTOOPA(BTOOPAConfig(wavelength=1550e-9, num_elements=64))
    bto_opa.set_steering_angle(15.0)
    
    print("\n1. Drive Voltage Comparison (for π phase shift):")
    print("-" * 50)
    print(f"  TFLN Vπ: ~20 V (thermal tuning)")
    print(f"  BTO Vπ:  {bto_opa.phase_shifters[0].v_pi:.3f} V")
    if bto_opa.phase_shifters[0].v_pi > 0:
        print(f"  Advantage: {20 / bto_opa.phase_shifters[0].v_pi:.1f}x lower voltage")
    else:
        print(f"  Advantage: N/A")
    
    print("\n2. Power Consumption (64-element array):")
    print("-" * 50)
    # Estimate TFLN power (thermal tuning)
    tfln_power_per_heater = 10e-3  # 10 mW per heater
    tfln_total = 64 * tfln_power_per_heater
    
    bto_total = bto_opa.get_total_power_consumption()
    
    print(f"  TFLN (thermal): ~{tfln_total*1e3:.0f} mW")
    print(f"  BTO (EO):       ~{bto_total*1e6:.1f} μW")
    if bto_total > 0:
        print(f"  Advantage: {tfln_total / bto_total:.0f}x lower power")
    else:
        print(f"  Advantage: infinite (static power ~0 for EO)")
    
    print("\n3. Switching Speed:")
    print("-" * 50)
    print(f"  TFLN (thermal): ~1-10 μs")
    print(f"  BTO (EO):       ~{bto_opa.phase_shifters[0].cfg.switching_time*1e12:.0f} ps")
    print(f"  Advantage: {(1e-6) / bto_opa.phase_shifters[0].cfg.switching_time:.0f}x faster")
    
    print("\n4. Technology Maturity:")
    print("-" * 50)
    print("  TFLN: Commercial PDKs available (CCRAFT, Luxtelligence)")
    print("  BTO:  Research only (UC Berkeley, ETH Zurich)")
    print("  Risk: BTO is 5-10 years from commercial PDK")
    
    print("\n  Note: Beam steering performance (directivity, sidelobes)")
    print("  is identical for both technologies — the difference is")
    print("  in drive electronics, power, and speed, not optics.")
    
    print("\n" + "=" * 70)
    print("Conclusion: BTO offers dramatically lower voltage and power,")
    print("with much faster switching, at the cost of technology maturity.")
    print("=" * 70)


if __name__ == "__main__":
    compare_tfln_vs_bto()
