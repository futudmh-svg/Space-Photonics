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

## What's Inside

| Technology | Status | Notes |
|-----------|--------|-------|
| TFLN OPA Phase Shifters | ✅ | Mature, thermal tuning |
| **BTO Phase Shifters** | ✅ **New** | 30x lower voltage, ps switching |
| Ag-Chalcogenide Amplifier | ✅ | All-optical gain |
| Nested Control (Optical PLL + Kalman) | ✅ | ns + μs loops |
| Atmospheric Channel | ✅ | Turbulence, scintillation |
| VLEO Thermal Model | ✅ | Atomic oxygen, aerothermal |

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

### `bto_phase_shifter.py` ⭐ NEW
Barium Titanate (BTO) phase shifters — alternative to TFLN:
- **900 pm/V** electro-optic coefficient (30x TFLN)
- **< 0.1 V·cm** drive voltage product
- **< 100 ps** switching (no thermal tuning)
- Compare TFLN vs BTO performance directly

```python
from twin.bto_phase_shifter import BTOOPA, BTOOPAConfig
from twin.opa_beamsteer import OPABeamSteerer, OPAConfig

# BTO OPA — much lower voltage
bto_opa = BTOOPA(BTOOPAConfig(num_elements=64))
bto_opa.set_steering_angle(15.0)

# Compare with TFLN
tfln_opa = OPABeamSteerer(OPAConfig(num_elements=64))
tfln_opa.set_steering_angle(15.0)
```

Run the comparison:
```bash
python3 -c "from twin.bto_phase_shifter import compare_tfln_vs_bto; compare_tfln_vs_bto()"
```

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
