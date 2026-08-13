"""
Unit tests for Space Photonics Digital Twin

Run with: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from space_photonics_twin import (
    OPABeamSteerer, OPAConfig,
    AgChalcogenideAmplifier, AgChalcogenideConfig,
    VLEOPropagator, HypersonicVehicle, OrbitConfig, VehicleConfig,
    DigitalTwin, TwinConfig,
    AtmosphericChannel, AtmosphericConfig,
    VLEOThermalModel, VLEOThermalConfig
)


class TestOPABeamSteerer:
    """Test OPA beam steering module."""
    
    def test_initialization(self):
        opa = OPABeamSteerer(OPAConfig())
        assert opa.cfg.num_elements == 64
        assert opa.cfg.wavelength == 1550e-9
        
    def test_steering_angle(self):
        opa = OPABeamSteerer(OPAConfig())
        opa.set_steering_angle(15.0, 0.0)
        assert np.isclose(opa.current_theta, np.radians(15.0))
        
    def test_farfield_pattern(self):
        opa = OPABeamSteerer(OPAConfig(num_elements=16))
        opa.set_steering_angle(10.0)
        theta_range = np.linspace(-30, 30, 100)
        intensity = opa.compute_farfield(np.radians(theta_range))
        assert len(intensity) == 100
        assert np.all(intensity >= 0)
        assert np.max(intensity) <= 1.0
        
    def test_beamwidth(self):
        opa = OPABeamSteerer(OPAConfig(num_elements=64, pitch=10e-6))
        bw = opa.get_beamwidth()
        assert bw > 0
        assert bw < 5.0  # Should be narrow for 64 elements


class TestAgChalcogenideAmplifier:
    """Test Ag-chalcogenide amplifier."""
    
    def test_initialization(self):
        amp = AgChalcogenideAmplifier(AgChalcogenideConfig())
        assert amp.cfg.small_signal_gain == 20
        
    def test_signal_processing(self):
        amp = AgChalcogenideAmplifier(AgChalcogenideConfig())
        p_out, phase = amp.process_signal(1e-3, 1550e-9)
        assert p_out > 1e-3  # Should have gain
        assert phase != 0.0  # Should have phase shift
        
    def test_saturation(self):
        amp = AgChalcogenideAmplifier(AgChalcogenideConfig(
            small_signal_gain=20,
            saturation_power=1e-3
        ))
        p_out_low, _ = amp.process_signal(1e-6, 1550e-9)
        p_out_high, _ = amp.process_signal(1e-2, 1550e-9)  # Well above saturation
        
        gain_low = p_out_low / 1e-6
        gain_high = p_out_high / 1e-2
        
        assert gain_low > gain_high  # High power should saturate
        
    def test_state(self):
        amp = AgChalcogenideAmplifier(AgChalcogenideConfig())
        state = amp.get_state()
        assert 'gain_db' in state
        assert 'phase_shift_rad' in state


class TestVLEOPropagator:
    """Test VLEO orbit propagation."""
    
    def test_initialization(self):
        sat = VLEOPropagator(OrbitConfig())
        assert sat.cfg.altitude == 300e3
        
    def test_propagation(self):
        sat = VLEOPropagator(OrbitConfig())
        pos0 = sat.get_position_ecef()
        sat.propagate(1.0)
        pos1 = sat.get_position_ecef()
        
        assert not np.allclose(pos0, pos1)
        
    def test_orbit_period(self):
        sat = VLEOPropagator(OrbitConfig(altitude=400e3))
        period = sat.period
        assert 5000 < period < 6000  # ~90 min for LEO


class TestHypersonicVehicle:
    """Test hypersonic vehicle model."""
    
    def test_propagation(self):
        veh = HypersonicVehicle(VehicleConfig())
        pos0 = veh.get_position_ecef()
        veh.propagate(1.0)
        pos1 = veh.get_position_ecef()
        
        assert not np.allclose(pos0, pos1)
        
    def test_slant_range(self):
        sat = VLEOPropagator(OrbitConfig())
        veh = HypersonicVehicle(VehicleConfig())
        
        sat_pos = sat.get_position_ecef()
        slant_range = veh.get_slant_range_to_satellite(sat_pos)
        
        assert slant_range > 0
        assert slant_range < 1e7  # Should be reasonable


class TestAtmosphericChannel:
    """Test atmospheric channel model."""
    
    def test_initialization(self):
        atm = AtmosphericChannel(AtmosphericConfig())
        assert atm.cfg.wavelength == 1550e-9
        
    def test_fried_parameter(self):
        atm = AtmosphericChannel(AtmosphericConfig())
        r0 = atm.compute_r0(45.0)
        assert r0 > 0
        assert r0 < 1.0  # Typical r0 is cm-scale
        
    def test_channel_application(self):
        atm = AtmosphericChannel(AtmosphericConfig())
        p_in = 1.0
        p_out = atm.apply_channel(p_in, 45.0)
        assert p_out >= 0
        assert p_out <= p_in * 2  # Scintillation can amplify or fade


class TestVLEOThermalModel:
    """Test VLEO thermal model."""
    
    def test_initialization(self):
        therm = VLEOThermalModel(VLEOThermalConfig())
        assert therm.cfg.altitude == 300e3
        
    def test_thermal_update(self):
        therm = VLEOThermalModel(VLEOThermalConfig())
        therm.update(1.0, sun_angle=45.0)
        assert therm.satellite_temp > 200
        assert therm.satellite_temp < 400
        
    def test_thermal_effects(self):
        therm = VLEOThermalModel(VLEOThermalConfig())
        effects = therm.get_thermal_effects_on_optics()
        assert 'opa_phase_drift_rad' in effects


class TestDigitalTwin:
    """Integration tests for full digital twin."""
    
    def test_initialization(self):
        twin = DigitalTwin(TwinConfig())
        assert twin.time == 0.0
        
    def test_single_step(self):
        twin = DigitalTwin(TwinConfig(dt=1e-6))
        twin.step()
        assert twin.time == 1e-6
        
    def test_short_simulation(self):
        twin = DigitalTwin(TwinConfig(dt=1e-6, log_interval=1e-3))
        twin.run(duration=0.01, progress_interval=None)
        assert len(twin.log_data) > 0
        
    def test_summary(self):
        twin = DigitalTwin(TwinConfig(dt=1e-6, log_interval=1e-3))
        twin.run(duration=0.01, progress_interval=None)
        summary = twin.get_summary()
        assert 'mean_snr_db' in summary
        
    def test_save_results(self, tmp_path):
        twin = DigitalTwin(TwinConfig(dt=1e-6, log_interval=1e-3))
        twin.run(duration=0.01, progress_interval=None)
        
        filepath = tmp_path / "test_results.json"
        twin.save_results(str(filepath))
        assert filepath.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
