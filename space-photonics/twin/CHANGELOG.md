# Changelog

## [0.3.0] - 2026-08-14

### Added
- **BTO Phase Shifters**: Barium Titanate (BaTiO₃) alternative to TFLN
  - 30x lower drive voltage (~mV vs ~20V)
  - Sub-100 ps switching (vs μs thermal tuning)
  - Direct TFLN vs BTO comparison utility
- **GitHub Codespaces**: One-click cloud development
  - `.devcontainer/devcontainer.json` with Python 3.11 + Jupyter
  - Auto-installs dependencies on launch
  - Pre-configured VS Code extensions

### Changed
- **README**: Added Codespaces badge and quick-start

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
