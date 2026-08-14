# SPACE_PHOTONICS.md — Knowledge Base & Reference Index

> Living document. Updated per session. DOIs are permanent.

---

## Core Technologies

### Multi-face Optical Phased Array (OPA)
- **Preferred platform:** TFLN (thin-film lithium niobate) for fast EO phase control
- **Routing:** Si₃N₄ for low-loss waveguide networks
- **Switching/amplification:** Ag-doped chalcogenide (Ag-Ge-In-S-CsI) for all-optical Kerr/FWM

### Material Property Quick Reference
| Material | n₂ (m²/W) | Loss (dB/cm) | Use Case |
|----------|-----------|--------------|----------|
| Si₃N₄ | ~2.6×10⁻¹⁹ | <0.1 | Low-loss routing |
| TFLN (x-cut) | ~1.6×10⁻¹⁹ | ~0.5 | Fast phase modulation |
| Ag-Ge-In-S-CsI | ~10⁻¹⁷–10⁻¹⁸ | ~1–3 | Nonlinear amplification |
| GeSbS | ~5×10⁻¹⁸ | ~0.5 | Mid-IR, nonlinear |

### Key Physics Reminders
- **All-optical single-photon detection is impossible** — use SPADs for quantum-limited detection.
- Kerr nonlinearity: Δn = n₂I
- FWM efficiency ∝ (n₂)² / (A_eff)² × L_eff²
- VLEO atmospheric extinction: strongly dependent on AOD, cloud fraction, elevation angle.

---

## Paper References

### OPA & Beam Steering
| DOI / arXiv | Title | Authors | Year | Notes |
|-------------|-------|---------|------|-------|
| | | | | |

### TFLN Photonics
| DOI / arXiv | Title | Authors | Year | Notes |
|-------------|-------|---------|------|-------|
| | | | | |

### Chalcogenide Nonlinear Photonics
| DOI / arXiv | Title | Authors | Year | Notes |
|-------------|-------|---------|------|-------|
| | | | | |

### VLEO / Hypersonic Tracking
| DOI / arXiv | Title | Authors | Year | Notes |
|-------------|-------|---------|------|-------|
| | | | | |

---

## Chinese Partners & Capabilities

| Institution | Specialty | Contact / Status |
|-------------|-----------|------------------|
| 哈工大 (HIT) | Laser comms, space-qualified systems | |
| 吉林大学 | OPA chips, silicon photonics | |
| 图灵量子 (TuringQ) | TFLN pilot line, foundry access | |
| 宁波大学 | Ag-chalcogenide growth & characterization | |
| 中山大学 | GeSbS waveguides, mid-IR | |

---

## Standards & Requirements

- **中国星网 (China Satellite Network)** laser comm specs:
  - 10G / 100G / 400G inter-satellite links
  - See: [add spec document link]

---

## Active Calculations

| File | Description | Status |
|------|-------------|--------|
| `calculations/vleo_triangulation.py` | VLEO-to-hypersonic link budget | TODO |

## Architecture Documents

| Document | Description |
|----------|-------------|
| `architecture/constellation_tracking.md` | Hypersonic target tracking via multi-satellite triangulation |
| `architecture/vleo_mega_constellation.md` | 500–2000 node VLEO photonic fabric: 3C integration, mesh networking, digital twin |
| `architecture/foundry_fabrication.md` | TFLN + Si₃N₄ + chalcogenide foundry flow, hybrid CMOS integration, radiation hardening |

---

*Last updated: 2026-08-15*
