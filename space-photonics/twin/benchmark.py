"""
Benchmark Digital Twin Performance

Measures simulation throughput and memory usage.
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from space_photonics_twin import DigitalTwin, TwinConfig


def benchmark_simulation(duration: float = 1.0, dt: float = 1e-6):
    """Benchmark simulation performance."""
    config = TwinConfig(dt=dt, log_interval=1e-3)
    twin = DigitalTwin(config)
    
    start_time = time.time()
    twin.run(duration=duration, progress_interval=None)
    end_time = time.time()
    
    wall_time = end_time - start_time
    sim_time = duration
    steps = int(duration / dt)
    
    throughput = steps / wall_time
    realtime_factor = sim_time / wall_time
    
    print(f"\nBenchmark Results:")
    print(f"  Simulation time: {sim_time:.3f} s")
    print(f"  Wall clock time: {wall_time:.3f} s")
    print(f"  Timestep: {dt:.2e} s")
    print(f"  Total steps: {steps:,}")
    print(f"  Throughput: {throughput:,.0f} steps/s")
    print(f"  Real-time factor: {realtime_factor:.1f}x")
    print(f"  Data points logged: {len(twin.log_data)}")
    
    return {
        'wall_time': wall_time,
        'throughput': throughput,
        'realtime_factor': realtime_factor
    }


def benchmark_scenarios():
    """Benchmark different scenarios."""
    scenarios = {
        'fast': TwinConfig(dt=1e-5, log_interval=1e-2, 
                          enable_nested_control=False, enable_thermal=False),
        'default': TwinConfig(dt=1e-6, log_interval=1e-3),
        'high_perf': TwinConfig(dt=1e-7, log_interval=1e-4,
                               enable_nested_control=True, enable_thermal=True)
    }
    
    print("="*60)
    print("Scenario Benchmark Comparison")
    print("="*60)
    
    results = {}
    for name, config in scenarios.items():
        print(f"\n{name.upper()}:")
        twin = DigitalTwin(config)
        
        start = time.time()
        twin.run(duration=1.0, progress_interval=None)
        wall_time = time.time() - start
        
        steps = int(1.0 / config.dt)
        throughput = steps / wall_time
        
        print(f"  dt={config.dt:.0e} | {throughput:,.0f} steps/s | {wall_time:.2f}s wall time")
        results[name] = throughput
    
    print("\n" + "="*60)
    print("Summary:")
    for name, throughput in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name:12s}: {throughput:>10,.0f} steps/s")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Digital Twin")
    parser.add_argument('--duration', type=float, default=1.0, help='Simulation duration')
    parser.add_argument('--dt', type=float, default=1e-6, help='Time step')
    parser.add_argument('--scenarios', action='store_true', help='Compare scenarios')
    
    args = parser.parse_args()
    
    if args.scenarios:
        benchmark_scenarios()
    else:
        benchmark_simulation(args.duration, args.dt)
