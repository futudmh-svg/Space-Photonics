"""
Space Photonics Digital Twin - Demo Script

Demonstrates the full simulation pipeline:
1. Initialize digital twin with default config
2. Run 10-second acquisition and tracking simulation
3. Save results and print summary
"""

import sys
import os

# Add twin module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from space_photonics_twin import DigitalTwin, TwinConfig


def main():
    print("=" * 60)
    print("Space Photonics Digital Twin - Demo")
    print("=" * 60)
    
    # Configuration
    config = TwinConfig(
        dt=1e-6,                    # 1 microsecond time step
        log_interval=1e-3,          # Log every millisecond
        tx_power=1.0,               # 1W transmit power
        wavelength=1550e-9,         # 1550 nm
        tx_aperture=0.1,            # 10 cm TX aperture
        rx_aperture=0.05,           # 5 cm RX aperture
        enable_tracking=True,
        tracking_bandwidth=1e3      # 1 kHz tracking loop
    )
    
    # Initialize twin
    print("\n[1/4] Initializing digital twin...")
    twin = DigitalTwin(config)
    
    # Run simulation
    print("[2/4] Running simulation...")
    twin.run(duration=10.0, progress_interval=1.0)
    
    # Save results
    print("\n[3/4] Saving results...")
    output_dir = os.path.join(os.path.dirname(__file__), '../results')
    os.makedirs(output_dir, exist_ok=True)
    twin.save_results(os.path.join(output_dir, 'simulation_results.json'))
    
    # Print summary
    print("\n[4/4] Simulation Summary:")
    print("-" * 40)
    summary = twin.get_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key:25s}: {value:10.3f}")
        else:
            print(f"  {key:25s}: {value}")
    
    print("\n" + "=" * 60)
    print("Demo complete. Results saved to results/simulation_results.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
