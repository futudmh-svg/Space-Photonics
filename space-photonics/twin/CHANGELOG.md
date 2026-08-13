# Changelog

## [0.2.0] - 2026-08-14

### Added
- **Control Loops**: Nested optical PLL (ns) + digital Kalman tracker (μs)
- **Atmospheric Channel**: Turbulence, scintillation, beam wander models
- **Thermal Model**: VLEO thermal environment with atomic oxygen heating
- **CLI**: Command-line interface with scenarios and config files
- **Config Manager**: JSON config load/save, 6 predefined scenarios
- **Parameter Sweep**: Design of experiments for optimization
- **Jupyter Notebook**: Interactive demo with plots
- **GitHub Actions**: CI workflow for Python 3.8-3.12
- **Unit Tests**: pytest suite for all modules

### Changed
- **Orchestrator**: Integrated all subsystems with nested control
- **README**: Updated architecture diagram and documentation

## [0.1.0] - 2026-08-14

### Added
- **OPA Beam Steerer**: Multi-face OPA with TFLN phase shifters
- **Ag-Chalcogenide Amplifier**: Kerr-based nonlinear amplification
- **Orbit/Target**: VLEO propagator + hypersonic vehicle model
- **Link Budget**: Optical link calculation with pointing loss
- **Visualization**: Matplotlib plots for SNR, power, pointing error
- **Demo Script**: Example simulation runner
