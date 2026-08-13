# Space Photonics Digital Twin v0.2.0

All-optical digital twin for VLEO satellite-to-hypersonic vehicle optical communication.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Digital Twin Core                                │
├─────────────────────────────────────────────────────────────────────────┤
│  VLEO Orbit      │  Hypersonic      │  OPA Beam    │  Ag-Chalcogenide  │
│  Propagator      │  Vehicle Model   │  Steering    │  Amplifier        │
├─────────────────────────────────────────────────────────────────────────┤
│  Nested Control Loops                                                  │
│  ├── Optical PLL (ns)                                                   │
│  └── Digital Kalman (μs)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Atmospheric Channel  │  VLEO Thermal Environment                       │
│  ├── Turbulence       │  ├── Atomic oxygen drag                         │
│  ├── Scintillation    │  ├── Solar radiation                            │
│  └── Beam wander      │  └── Aerothermal heating                        │
├─────────────────────────────────────────────────────────────────────────┤
│              Optical Link Budget + Tracking                              │
├─────────────────────────────────────────────────────────────────────────┤
│              Data Logging + Visualization                                │
└─────────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd space-photonics/twin
pip install -e .
# Or for development:
pip install -e ".[dev]"
```

## Quick Start

### Python Script
```python
from space_photonics_twin import DigitalTwin, TwinConfig

config = TwinConfig(
    dt=1e-6,
    tx_power=1.0,
    wavelength=1550e-9,
    enable_tracking=True,
    enable_thermal=True,
    enable_nested_control=True
)

twin = DigitalTwin(config)
twin.run(duration=10.0)
twin.save_results("results.json")
```

### Jupyter Notebook
```bash
jupyter notebook twin_demo.ipynb
```

### Demo Script
```bash
python demo.py
python visualize.py results/simulation_results.json plots/
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

### `control_loop.py`
Nested tracking loops:
- **Optical PLL**: All-optical phase-locked loop (ns-timescale)
- **Digital Kalman**: Trajectory prediction with lead-ahead (μs-timescale)

### `atmospheric_channel.py`
Atmospheric optical channel:
- Log-normal scintillation
- Tilt/angle-of-arrival fluctuations
- Beam wander
- Aperture averaging
- Extinction model

### `thermal_model.py`
VLEO thermal environment:
- Atomic oxygen drag heating
- Solar radiation
- Earth IR and albedo
- Aerothermal heating
- Radiative cooling
- Active heater control

### `twin_orchestrator.py`
Main simulation controller integrating all subsystems.

## Running Tests

```bash
pytest tests/ -v
```

## Requirements

- Python 3.8+
- numpy
- matplotlib
- pytest (for tests)
- jupyter (for notebooks)

## License

MIT
