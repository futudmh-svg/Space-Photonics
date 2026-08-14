# Space Photonics Digital Twin

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=futudmh-svg/Space-Photonics)

All-optical digital twin for VLEO satellite-to-hypersonic vehicle optical communication.

## Quick Start

Click the badge above to open this repo in GitHub Codespaces — everything is pre-installed.

Or run locally:

```bash
git clone https://github.com/futudmh-svg/Space-Photonics.git
cd Space-Photonics/space-photonics/twin
pip install -e .
python3 -m twin --scenario tracking --duration 10.0
```

## What's Inside

| Technology | Status |
|-----------|--------|
| TFLN OPA Phase Shifters | ✅ Implemented |
| **BTO Phase Shifters** | ✅ **New** — 30x lower voltage, ps switching |
| Ag-Chalcogenide Amplifier | ✅ Implemented |
| Nested Control (Optical PLL + Kalman) | ✅ Implemented |
| Atmospheric Channel | ✅ Implemented |
| VLEO Thermal Model | ✅ Implemented |

## Repository Structure

```
Space-Photonics/
├── space-photonics/
│   ├── twin/              # Digital twin package
│   ├── architecture/      # System architecture docs
│   └── calculations/      # Standalone link budget
├── .devcontainer/         # Codespaces configuration
└── README.md
```

## Documentation

- [Twin Tutorial](space-photonics/twin/TUTORIAL.md)
- [API Reference](space-photonics/twin/generate_docs.py)
- [Changelog](space-photonics/twin/CHANGELOG.md)

## License

MIT
