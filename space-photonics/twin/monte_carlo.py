"""
Monte Carlo Analysis

Run multiple simulations with randomized parameters
to assess link reliability and performance statistics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import json
from pathlib import Path
from tqdm import tqdm

from space_photonics_twin import DigitalTwin, TwinConfig


def run_monte_carlo(
    n_runs: int = 100,
    duration: float = 1.0,
    param_distributions: dict = None,
    output_dir: str = "monte_carlo_results"
) -> dict:
    """
    Run Monte Carlo simulation.
    
    Args:
        n_runs: Number of simulation runs
        duration: Duration per run [s]
        param_distributions: Dict of parameter sampling functions
        output_dir: Output directory
        
    Returns:
        Statistics dict
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Default distributions
    if param_distributions is None:
        param_distributions = {
            'tx_power': lambda: np.random.uniform(0.5, 2.0),
            'atmospheric_loss_db': lambda: np.random.uniform(1.0, 5.0),
            'pointing_loss_db': lambda: np.random.uniform(1.0, 5.0)
        }
    
    results = []
    
    print(f"Running {n_runs} Monte Carlo simulations...")
    
    for i in tqdm(range(n_runs)):
        # Sample parameters
        params = {k: v() for k, v in param_distributions.items()}
        
        # Create config with sampled parameters
        config = TwinConfig(**params)
        
        # Run simulation
        twin = DigitalTwin(config)
        twin.run(duration=duration, progress_interval=None)
        
        # Collect metrics
        summary = twin.get_summary()
        
        result = {
            'run_id': i,
            'parameters': params,
            'metrics': summary
        }
        results.append(result)
    
    # Compute statistics
    snrs = [r['metrics']['mean_snr_db'] for r in results if 'mean_snr_db' in r['metrics']]
    rx_powers = [r['metrics']['mean_rx_power_dbm'] for r in results if 'mean_rx_power_dbm' in r['metrics']]
    
    stats = {
        'n_runs': n_runs,
        'snr': {
            'mean': np.mean(snrs),
            'std': np.std(snrs),
            'min': np.min(snrs),
            'max': np.max(snrs),
            'p10': np.percentile(snrs, 10),
            'p50': np.percentile(snrs, 50),
            'p90': np.percentile(snrs, 90)
        },
        'rx_power': {
            'mean': np.mean(rx_powers),
            'std': np.std(rx_powers),
            'min': np.min(rx_powers),
            'max': np.max(rx_powers)
        },
        'link_availability': np.mean([s > 10 for s in snrs])  # SNR > 10 dB
    }
    
    # Save results
    with open(f"{output_dir}/monte_carlo_results.json", 'w') as f:
        json.dump({'statistics': stats, 'runs': results}, f, indent=2)
    
    print(f"\nMonte Carlo Results:")
    print(f"  Link availability (SNR>10dB): {stats['link_availability']*100:.1f}%")
    print(f"  Mean SNR: {stats['snr']['mean']:.2f} ± {stats['snr']['std']:.2f} dB")
    print(f"  SNR range: [{stats['snr']['min']:.1f}, {stats['snr']['max']:.1f}] dB")
    print(f"  SNR P90: {stats['snr']['p90']:.2f} dB")
    
    return stats


def analyze_sensitivity(n_runs: int = 50):
    """
    Sensitivity analysis: vary one parameter at a time.
    """
    print("="*60)
    print("Sensitivity Analysis")
    print("="*60)
    
    base_config = TwinConfig()
    
    # Parameters to test
    param_ranges = {
        'tx_power': [0.1, 0.5, 1.0, 2.0, 5.0],
        'tx_aperture': [0.03, 0.05, 0.1, 0.2, 0.3],
        'wavelength': [1064e-9, 1310e-9, 1550e-9, 2000e-9],
        'atmospheric_loss_db': [0.5, 1.0, 2.0, 3.0, 5.0]
    }
    
    for param_name, values in param_ranges.items():
        print(f"\n{param_name}:")
        print("-"*40)
        
        snrs = []
        for val in values:
            kwargs = {param_name: val}
            config = TwinConfig(**kwargs)
            
            twin = DigitalTwin(config)
            twin.run(duration=0.5, progress_interval=None)
            
            summary = twin.get_summary()
            snr = summary.get('mean_snr_db', 0)
            snrs.append(snr)
            
            print(f"  {val:>12.4f} -> SNR={snr:.2f} dB")
        
        # Compute sensitivity
        sensitivity = (snrs[-1] - snrs[0]) / (values[-1] - values[0])
        print(f"  Sensitivity: {sensitivity:.2f} dB per unit")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monte Carlo Analysis")
    parser.add_argument('--runs', type=int, default=100, help='Number of runs')
    parser.add_argument('--duration', type=float, default=1.0, help='Duration per run')
    parser.add_argument('--sensitivity', action='store_true', help='Run sensitivity analysis')
    
    args = parser.parse_args()
    
    if args.sensitivity:
        analyze_sensitivity()
    else:
        run_monte_carlo(n_runs=args.runs, duration=args.duration)
