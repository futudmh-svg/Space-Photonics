# Space Photonics Digital Twin

All-optical digital twin for VLEO satellite-to-hypersonic vehicle optical communication.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Digital Twin Core                         │
├─────────────────────────────────────────────────────────────┤
│  VLEO Orbit      │  Hypersonic      │  OPA Beam    │  Ag-Chalcogenide │
│  Propagator      │  Vehicle Model   │  Steering    │  Amplifier       │
├─────────────────────────────────────────────────────────────┤
│              Optical Link Budget + Tracking                  │
├─────────────────────────────────────────────────────────────┤
│              Data Logging + Visualization                    │
└─────────────────────────────────────────────────────────────┘
```

## Components

### `opa_beamsteer.py`
Multi-face optical phased array with TFLN phase shifters:
- Far-field pattern computation
- Phase quantization effects
- Thermal drift modeling
- Pointing error estimation

### `agchalcogenide.py`
Silver-doped chalcogenide all-optical amplifier:
- Kerr nonlinear phase shift
- Four-wave mixing gain
- Silver migration dynamics
- Saturation effects

### `orbit_target.py`
Orbital mechanics and target tracking:
- VLEO two-body propagator
- Hypersonic vehicle trajectory
- Slant range and elevation geometry
- Azimuth calculation

### `twin_orchestrator.py`
Main simulation controller integrating all subsystems.

## Quick Start

```bash
# Run demo simulation
cd space-photonics/twin
python demo.py

# Generate plots from results
python visualize.py ../results/simulation_results.json plots/
```

## Python Usage

```python
from space_photonics_twin import DigitalTwin, TwinConfig

config = TwinConfig(
    dt=1e-6,
    tx_power=1.0,
    wavelength=1550e-9,
    enable_tracking=True
)

twin = DigitalTwin(config)
twin.run(duration=10.0)
twin.save_results("results.json")
```

## Requirements

- Python 3.8+
- numpy
- matplotlib (for visualization)
