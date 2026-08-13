#!/usr/bin/env python3
"""
Space Photonics Digital Twin - Command Line Interface

Usage:
    python -m space_photonics_twin.cli --scenario tracking --duration 10.0
    python -m space_photonics_twin.cli --config my_config.json --output results.json
"""

import argparse
import sys
from pathlib import Path

from . import (
    DigitalTwin, TwinConfig,
    get_scenario, list_scenarios,
    load_config, save_config
)


def main():
    parser = argparse.ArgumentParser(
        description="Space Photonics Digital Twin CLI"
    )
    
    parser.add_argument(
        '--scenario', '-s',
        choices=list_scenarios(),
        help='Use predefined scenario configuration'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Load configuration from JSON file'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=float,
        default=10.0,
        help='Simulation duration in seconds (default: 10.0)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results.json',
        help='Output file for results (default: results.json)'
    )
    
    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Generate plots after simulation'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        print(f"Loading config from {args.config}")
        config = load_config(args.config)
    elif args.scenario:
        print(f"Using scenario: {args.scenario}")
        config = get_scenario(args.scenario)
    else:
        print("Using default configuration")
        config = TwinConfig()
    
    # Run simulation
    print(f"\nRunning simulation for {args.duration}s...")
    twin = DigitalTwin(config)
    twin.run(duration=args.duration, progress_interval=1.0 if args.verbose else None)
    
    # Save results
    twin.save_results(args.output)
    
    # Print summary
    summary = twin.get_summary()
    print("\n" + "="*60)
    print("Simulation Summary")
    print("="*60)
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    print(f"    {k}: {v:.3f}")
                else:
                    print(f"    {k}: {v}")
        elif isinstance(value, float):
            print(f"  {key:25s}: {value:10.3f}")
        else:
            print(f"  {key:25s}: {value}")
    
    # Generate plots if requested
    if args.plot:
        try:
            from .visualize import generate_all_plots
            plot_dir = Path(args.output).parent / 'plots'
            generate_all_plots(args.output, str(plot_dir))
        except ImportError:
            print("Warning: matplotlib not available, skipping plots")
    
    print(f"\nResults saved to {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
