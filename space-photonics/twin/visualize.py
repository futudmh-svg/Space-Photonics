"""
Visualization utilities for digital twin results.

Plots:
- SNR vs time
- Received power vs time
- Pointing error vs time
- Satellite ground track
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path


def load_results(filepath: str) -> dict:
    """Load simulation results from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def plot_snr(data: list, output_path: str):
    """Plot SNR vs time."""
    times = [d['time'] for d in data]
    snrs = [d['optical']['snr_db'] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times, snrs, 'b-', linewidth=0.8)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('SNR [dB]')
    ax.set_title('Optical Link SNR')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, max(times)])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_rx_power(data: list, output_path: str):
    """Plot received power vs time."""
    times = [d['time'] for d in data]
    rx_power = [d['optical']['rx_power_dbm'] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times, rx_power, 'g-', linewidth=0.8)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Received Power [dBm]')
    ax.set_title('Optical Received Power')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, max(times)])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_pointing_error(data: list, output_path: str):
    """Plot pointing error vs time."""
    times = [d['time'] for d in data]
    errors = [d['optical']['pointing_error'] for d in data]
    beamwidths = [d['optical']['beamwidth'] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times, errors, 'r-', linewidth=0.8, label='Pointing Error')
    ax.plot(times, beamwidths, 'k--', linewidth=1.0, label='Beamwidth')
    ax.plot(times, [bw/10 for bw in beamwidths], 'k:', linewidth=1.0, label='Beamwidth/10')
    
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Angle [deg]')
    ax.set_title('OPA Pointing Performance')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xlim([0, max(times)])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_orbit_3d(data: list, output_path: str):
    """Plot satellite orbit in 3D."""
    x = [d['satellite']['x'] / 1e3 for d in data]  # km
    y = [d['satellite']['y'] / 1e3 for d in data]
    z = [d['satellite']['z'] / 1e3 for d in data]
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Earth sphere (simplified)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    earth_r = 6371  # km
    x_earth = earth_r * np.outer(np.cos(u), np.sin(v))
    y_earth = earth_r * np.outer(np.sin(u), np.sin(v))
    z_earth = earth_r * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.2, color='blue')
    
    # Satellite orbit
    ax.plot(x, y, z, 'r-', linewidth=1.0, label='Satellite Orbit')
    ax.scatter([x[0]], [y[0]], [z[0]], color='green', s=50, label='Start')
    
    ax.set_xlabel('X [km]')
    ax.set_ylabel('Y [km]')
    ax.set_zlabel('Z [km]')
    ax.set_title('VLEO Satellite Orbit')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_plots(results_path: str, output_dir: str):
    """Generate all plots from results file."""
    print(f"Loading results from {results_path}...")
    results = load_results(results_path)
    data = results['results']
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\nGenerating plots in {output_dir}...")
    plot_snr(data, f"{output_dir}/snr_vs_time.png")
    plot_rx_power(data, f"{output_dir}/rx_power_vs_time.png")
    plot_pointing_error(data, f"{output_dir}/pointing_error_vs_time.png")
    plot_orbit_3d(data, f"{output_dir}/orbit_3d.png")
    
    print("\nAll plots generated successfully!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <results.json> [output_dir]")
        sys.exit(1)
    
    results_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "plots"
    
    generate_all_plots(results_path, output_dir)
