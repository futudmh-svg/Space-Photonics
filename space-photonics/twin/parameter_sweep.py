"""
Parameter Sweep Utility

Run design of experiments on digital twin parameters
to optimize optical link performance.
"""

import numpy as np
import json
from typing import Dict, List, Tuple
from dataclasses import asdict
from pathlib import Path
import itertools

from space_photonics_twin import DigitalTwin, TwinConfig


def run_sweep(
    param_grid: Dict[str, List],
    duration: float = 1.0,
    output_dir: str = "sweep_results"
) -> List[Dict]:
    """
    Run parameter sweep over digital twin configuration.
    
    Args:
        param_grid: Dict of parameter names to lists of values
        duration: Simulation duration per run [s]
        output_dir: Directory to save results
        
    Returns:
        List of result dicts with parameters and metrics
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate all combinations
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    combinations = list(itertools.product(*param_values))
    
    results = []
    
    print(f"Running {len(combinations)} parameter combinations...")
    
    for i, values in enumerate(combinations):
        # Build config from base
        config_kwargs = dict(zip(param_names, values))
        config = TwinConfig(**config_kwargs)
        
        # Run simulation
        twin = DigitalTwin(config)
        twin.run(duration=duration, progress_interval=None)
        
        # Get metrics
        summary = twin.get_summary()
        
        result = {
            'run_id': i,
            'parameters': config_kwargs,
            'metrics': summary
        }
        results.append(result)
        
        print(f"[{i+1}/{len(combinations)}] "
              f"SNR={summary['mean_snr_db']:.1f}dB | "
              f"params={config_kwargs}")
    
    # Save all results
    with open(f"{output_dir}/sweep_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSweep complete. Results saved to {output_dir}/sweep_results.json")
    return results


def find_optimal(results: List[Dict], metric: str = 'mean_snr_db', 
                 maximize: bool = True) -> Dict:
    """
    Find optimal parameter set from sweep results.
    
    Args:
        results: List of result dicts from run_sweep
        metric: Metric to optimize
        maximize: True to maximize, False to minimize
        
    Returns:
        Best result dict
    """
    if maximize:
        best = max(results, key=lambda x: x['metrics'].get(metric, -np.inf))
    else:
        best = min(results, key=lambda x: x['metrics'].get(metric, np.inf))
    
    return best


def print_sweep_summary(results: List[Dict]):
    """Print summary statistics from sweep."""
    snrs = [r['metrics']['mean_snr_db'] for r in results if 'mean_snr_db' in r['metrics']]
    
    print("\n" + "="*60)
    print("Parameter Sweep Summary")
    print("="*60)
    print(f"Total runs: {len(results)}")
    print(f"Mean SNR: {np.mean(snrs):.2f} dB")
    print(f"Best SNR: {np.max(snrs):.2f} dB")
    print(f"Worst SNR: {np.min(snrs):.2f} dB")
    print(f"SNR std: {np.std(snrs):.2f} dB")
    
    best = find_optimal(results)
    print(f"\nOptimal parameters:")
    for k, v in best['parameters'].items():
        print(f"  {k}: {v}")
    print(f"  -> {best['metrics']}")


if __name__ == "__main__":
    # Example: Sweep TX power and wavelength
    param_grid = {
        'tx_power': [0.5, 1.0, 2.0],
        'wavelength': [1064e-9, 1550e-9, 2000e-9],
        'tx_aperture': [0.05, 0.1, 0.2],
    }
    
    results = run_sweep(param_grid, duration=0.5)
    print_sweep_summary(results)
