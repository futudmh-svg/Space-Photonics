# Space Photonics Digital Twin - Tutorial

## Getting Started

### Installation

```bash
cd space-photonics/twin
pip install -e ".[dev]"
```

### Running Your First Simulation

```python
from space_photonics_twin import DigitalTwin, TwinConfig

# Create configuration
config = TwinConfig(
    dt=1e-6,              # 1 microsecond timestep
    duration=10.0,         # 10 second simulation
    enable_tracking=True   # Enable beam tracking
)

# Initialize and run
twin = DigitalTwin(config)
twin.run(duration=10.0)

# Save results
twin.save_results("my_first_sim.json")
```

### Using Predefined Scenarios

```python
from space_photonics_twin import get_scenario, list_scenarios

# List available scenarios
print(list_scenarios())
# ['default', 'high_performance', 'fast', 'acquisition', 'tracking', 'thermal_stress']

# Use a scenario
config = get_scenario('tracking')
twin = DigitalTwin(config)
twin.run(duration=5.0)
```

### Command Line Usage

```bash
# Run with default config
python -m space_photonics_twin --duration 10.0

# Use a scenario
python -m space_photonics_twin --scenario tracking --duration 5.0

# Load custom config
python -m space_photonics_twin --config configs/default.json --output results.json

# Generate plots
python -m space_photonics_twin --scenario tracking --plot
```

## Advanced Usage

### Parameter Sweep

```python
from space_photonics_twin.parameter_sweep import run_sweep

param_grid = {
    'tx_power': [0.5, 1.0, 2.0],
    'wavelength': [1064e-9, 1550e-9]
}

results = run_sweep(param_grid, duration=1.0)
```

### Monte Carlo Analysis

```python
from space_photonics_twin.monte_carlo import run_monte_carlo

stats = run_monte_carlo(n_runs=1000, duration=1.0)
print(f"Link availability: {stats['link_availability']*100:.1f}%")
```

### Custom Configuration File

Create `my_config.json`:
```json
{
  "dt": 1e-06,
  "tx_power": 2.0,
  "wavelength": 1.55e-06,
  "enable_tracking": true,
  "enable_thermal": true
}
```

Load it:
```python
from space_photonics_twin import load_config

config = load_config('my_config.json')
twin = DigitalTwin(config)
```

## Visualization

```bash
# After running simulation
python visualize.py results/simulation_results.json plots/
```

This generates:
- `snr_vs_time.png` - SNR timeline
- `rx_power_vs_time.png` - Received power
- `pointing_error_vs_time.png` - Tracking performance
- `orbit_3d.png` - Satellite trajectory

## Hardware-in-the-Loop

```python
from space_photonics_twin.hil_interface import HILInterface, HILConfig

hil = HILInterface(HILConfig())

# Register your hardware callbacks
hil.register_phase_sensor(my_phase_sensor)
hil.register_steering_actuator(my_opa_controller)

hil.start()
# ... run simulation with hardware
hil.stop()
```

## Exporting Results

```bash
# Export to CSV for MATLAB/Excel
python export.py results/simulation_results.json --csv results.csv

# Generate summary report
python export.py results/simulation_results.json --summary report.txt
```

## Troubleshooting

### Simulation is slow
- Increase `dt` (e.g., 1e-5 instead of 1e-6)
- Use `get_fast_config()` scenario
- Disable thermal and nested control

### Out of memory
- Reduce `log_interval` (log less frequently)
- Run shorter durations
- Clear buffer periodically with `streamer.clear_buffer()`

### Import errors
- Ensure you're in the `space-photonics/twin` directory
- Install with `pip install -e .`
- Check Python version >= 3.8
