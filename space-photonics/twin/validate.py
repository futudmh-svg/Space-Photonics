"""
Validate Digital Twin against standalone link budget calculator.

Compares results from the digital twin with the existing
vleo_triangulation.py calculations to ensure consistency.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from space_photonics_twin import DigitalTwin, TwinConfig

# Import standalone calculator
from calculations.vleo_triangulation import link_budget, aperture_gain


def compare_link_budget():
    """Compare digital twin link budget with standalone calculator."""
    
    # Common parameters
    wavelength = 1550e-9
    tx_power = 1.0
    tx_aperture = 0.1
    rx_aperture = 0.05
    altitude = 300e3
    elevation = 30.0
    
    # Standalone calculation
    tx_gain = aperture_gain(tx_aperture, wavelength)
    rx_gain = aperture_gain(rx_aperture, wavelength)
    slant_range = altitude / np.sin(np.radians(elevation))
    tx_power_dbm = 10 * np.log10(tx_power * 1000)
    
    standalone_result = link_budget(
        tx_power_dbm=tx_power_dbm,
        tx_gain_db=tx_gain,
        rx_gain_db=rx_gain,
        range_m=slant_range,
        wavelength_m=wavelength,
        elevation_deg=elevation
    )
    
    # Digital twin calculation
    config = TwinConfig(
        dt=1e-6,
        log_interval=1e-3,
        tx_power=tx_power,
        wavelength=wavelength,
        tx_aperture=tx_aperture,
        rx_aperture=rx_aperture,
        enable_tracking=False,  # Disable pointing errors for fair comparison
        atmospheric_loss_db=0.0  # Disable atmospheric loss for fair comparison
    )
    
    twin = DigitalTwin(config)
    twin.run(duration=0.01, progress_interval=None)
    
    # Get first data point (should be at t=0)
    if twin.log_data:
        twin_rx = twin.log_data[0]['optical']['rx_power_dbm']
    else:
        twin_rx = -np.inf
    
    # Compare
    standalone_rx = standalone_result['received_power_dbm']
    
    print("="*60)
    print("Link Budget Validation")
    print("="*60)
    print(f"\nParameters:")
    print(f"  Wavelength: {wavelength*1e9:.0f} nm")
    print(f"  TX Power: {tx_power} W")
    print(f"  TX Aperture: {tx_aperture*100:.0f} cm")
    print(f"  RX Aperture: {rx_aperture*100:.0f} cm")
    print(f"  Altitude: {altitude/1e3:.0f} km")
    print(f"  Elevation: {elevation}°")
    
    print(f"\nStandalone Calculator:")
    print(f"  FSPL: {standalone_result['fspl_db']:.2f} dB")
    print(f"  TX Gain: {standalone_result['tx_gain_db']:.2f} dBi")
    print(f"  RX Gain: {standalone_result['rx_gain_db']:.2f} dBi")
    print(f"  Received Power: {standalone_rx:.2f} dBm")
    
    print(f"\nDigital Twin:")
    print(f"  Received Power: {twin_rx:.2f} dBm")
    
    print(f"\nDifference: {abs(standalone_rx - twin_rx):.2f} dB")
    
    if abs(standalone_rx - twin_rx) < 1.0:
        print("✓ PASS: Results match within 1 dB")
    else:
        print("✗ FAIL: Results differ by more than 1 dB")
    
    return standalone_rx, twin_rx


def validate_pointing_loss():
    """Validate pointing loss model."""
    print("\n" + "="*60)
    print("Pointing Loss Validation")
    print("="*60)
    
    config = TwinConfig(
        dt=1e-6,
        log_interval=1e-3,
        enable_tracking=True
    )
    
    twin = DigitalTwin(config)
    twin.run(duration=0.1, progress_interval=None)
    
    # Check that pointing error decreases over time
    if len(twin.log_data) > 1:
        initial_error = twin.log_data[0]['optical']['pointing_error']
        final_error = twin.log_data[-1]['optical']['pointing_error']
        
        print(f"\nInitial pointing error: {initial_error:.4f}°")
        print(f"Final pointing error: {final_error:.4f}°")
        
        if final_error < initial_error:
            print("✓ PASS: Tracking improves pointing accuracy")
        else:
            print("? INFO: Pointing error stable or increasing (check convergence)")


if __name__ == "__main__":
    print("Space Photonics Digital Twin - Validation\n")
    
    compare_link_budget()
    validate_pointing_loss()
    
    print("\n" + "="*60)
    print("Validation complete")
    print("="*60)
