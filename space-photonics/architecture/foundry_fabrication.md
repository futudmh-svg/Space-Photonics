# Foundry Fabrication Roadmap: All-Optical Photonic Devices

## Overview

This document outlines the manufacturing pathway for the all-optical devices required by the VLEO photonic constellation: multi-face OPAs, chalcogenide nonlinear switches, Si₃N₄ routing meshes, and hybrid photonic-electronic packages. The goal is a domestic, radiation-tolerant foundry flow compatible with space qualification.

---

## Device Portfolio

| Device | Material Platform | Function | TRL Target |
|--------|------------------|----------|------------|
| Multi-face OPA | TFLN + Si₃N₄ | Beam steering, fast switching | TRL 6–7 |
| All-optical switch | Ag-Ge-In-S-CsI | Kerr/XPM gating, routing | TRL 4–5 |
| Low-loss mesh | Si₃N₄ | Waveguide routing, AWGR | TRL 7–8 |
| Photonic accelerator | Si₃N₄ MZI + Ag-chalc. | Matrix-vector multiplication | TRL 3–4 |
| SPAD array | InGaAs/InP | Quantum-limited detection | TRL 8 |
| Hybrid package | All above + CMOS | Full transceiver node | TRL 5–6 |

---

## Foundry Flow: TFLN + Si₃N₄ Platform

### Wafer Stack (Cross-Section)

```
        ┌─────────────────────────────────────┐
        │          Bond pads (Al/Cu)          │  ← Metal 3
        │  ┌───┐    ┌───┐    ┌───┐    ┌───┐  │
        │  │ O │    │ O │    │ O │    │ O │  │  ← Vias to heaters
        │  └───┘    └───┘    └───┘    └───┘  │
        ├─────────────────────────────────────┤
        │      Si heater / TiN traces         │  ← Metal 2
        ├─────────────────────────────────────┤
        │  ┌───────────────────────────────┐  │
        │  │      TFLN (300–600 nm)        │  │  ← Active layer: EO modulation
        │  │   x-cut, Z-propagating          │  │
        │  └───────────────────────────────┘  │
        ├─────────────────────────────────────┤
        │      Si₃N₄ (200–400 nm, LPCVD)      │  ← Low-loss routing
        ├─────────────────────────────────────┤
        │      SiO₂ BOX (2–4 μm, thermal)     │  ← Buried oxide
        ├─────────────────────────────────────┤
        │      Si handle wafer (725 μm)       │  ← Substrate
        └─────────────────────────────────────┘
                    Cross-section view
```

### Process Flow

```
┌─────────────────┐
│  START: Si wafer │
│  + thermal SiO₂  │
└────────┬────────┘
         ▼
┌─────────────────┐     ┌─────────────────┐
│  LPCVD Si₃N₄    │────►│  Si₃N₄ etch     │
│  (waveguide core)│     │  (CF₄/CHF₃ ICP) │
└─────────────────┘     └────────┬────────┘
                                 ▼
┌─────────────────┐     ┌─────────────────┐
│  TFLN bonding   │◄────│  Cladding SiO₂  │
│  (Wafer-to-wafer)│     │  (PECVD / TEOS) │
└────────┬────────┘     └─────────────────┘
         ▼
┌─────────────────┐
│  TFLN thinning  │
│  (CMP to 300nm) │
└────────┬────────┘
         ▼
┌─────────────────┐     ┌─────────────────┐
│  TFLN etch      │────►│  Heater deposit │
│  (Ar⁺ ion mill) │     │  (TiN / NiCr)   │
└─────────────────┘     └────────┬────────┘
                                 ▼
┌─────────────────┐     ┌─────────────────┐
│  Passivation    │◄────│  Metal stack    │
│  (SiO₂/Si₃N₄)   │     │  (Al/Cu RDL)    │
└────────┬────────┘     └─────────────────┘
         ▼
┌─────────────────┐
│  Dicing + facet │
│  polish / coat  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  TEST: optical  │
│  + electrical   │
└─────────────────┘
```

### Critical Process Parameters

| Step | Parameter | Spec | Tolerance |
|------|-----------|------|-----------|
| Si₃N₄ thickness | 300 nm | ±5 nm | Waveguide height |
| Si₃N₄ width | 800 nm | ±20 nm | Single-mode condition |
| TFLN thickness | 500 nm | ±25 nm | Vπ·L product |
| TFLN etch depth | 300 nm | ±15 nm | Sidewall angle >80° |
| Heater resistance | 500 Ω | ±50 Ω | Power consumption |
| Metal line width | 2 μm | ±0.2 μm | Current density |
| Waveguide loss | <0.1 dB/cm | — | At 1550 nm |
| Propagation loss (TFLN) | <0.5 dB/cm | — | After thinning |

---

## Foundry Flow: Ag-Doped Chalcogenide

### Material System: Ag-Ge-In-S-CsI

```
┌─────────────────────────────────────────┐
│         Chalcogenide deposition          │
│                                          │
│   Method: Thermal evaporation +          │
│           in-situ Ag photodoping         │
│                                          │
│   Composition:                           │
│   Ge₂₀In₅S₇₅ + CsI (5 at%) + Ag (1–3%) │
│                                          │
│   Substrate: Si₃N₄ on SiO₂/Si            │
│   or TFLN-clad waveguide                 │
│                                          │
│   Target thickness: 1–3 μm               │
│   Refractive index: n ≈ 2.4 @ 1550 nm    │
│   n₂: ~10⁻¹⁷–10⁻¹⁸ m²/W                 │
└─────────────────────────────────────────┘
```

### Fabrication Steps

1. **Substrate prep** — Clean Si₃N₄ waveguide surface, O₂ plasma activation
2. **Co-evaporation** — Ge, In, S from separate sources; CsI from effusion cell
3. **Ag photodoping** — Expose to 405 nm LED during/after deposition; Ag⁺ migrates into glass matrix
4. **Annealing** — 150°C N₂ ambient, 2 hr (reduce stress, stabilize n₂)
5. **Waveguide definition** — Lift-off or dry etch (CH₄/H₂ ICP) to form ridge waveguides
6. **Cladding** — SiO₂ PECVD or Al₂O₃ ALD for protection
7. **Facet polish** — Ion beam polishing for end-fire coupling

### Nonlinear Characterization

| Test | Method | Acceptance |
|------|--------|------------|
| n₂ measurement | Z-scan or SPM | >5×10⁻¹⁸ m²/W |
| FWM efficiency | Degenerate pump-probe | >-20 dB at 100 mW |
| XPM switching | Pump-probe time-resolved | <1 ps, contrast >10 dB |
| Optical damage threshold | CW + pulsed | >500 MW/cm² |
| Aging (85°C/85% RH, 1000 hr) | Accelerated life | <10% n₂ degradation |

---

## Hybrid Integration: Photonics + CMOS

### 3D Stacking Approach

```
┌─────────────────────────────────────────┐
│         CMOS CONTROL DIE (top)           │
│   ┌─────────────────────────────────┐   │
│   │  ADC/DAC  │  DSP  │  Memory     │   │
│   │  (12-bit) │(1 TFLOPS)│ (LPDDR)  │   │
│   └─────────────────────────────────┘   │
│              ┌─────────┐                │
│              │ μbumps  │  ← Cu pillar, 40 μm pitch
│              │(TSV)    │                │
│              └────┬────┘                │
├───────────────────┼─────────────────────┤
│    INTERPOSER     │    (Si or glass)    │
│   ┌───────────────┼───────────────┐     │
│   │  TSV / RDL    │   TSV / RDL   │     │
│   └───────────────┼───────────────┘     │
│                   │                     │
├───────────────────┼─────────────────────┤
│         PHOTONIC DIE (bottom)            │
│   ┌─────────────────────────────────┐   │
│   │  OPA  │  Switch  │  Si₃N₄ mesh  │   │
│   │  array│  matrix  │  + chalc.    │   │
│   └─────────────────────────────────┘   │
│              ┌─────────┐                │
│              │  Facet  │  ← Fiber or lens attach
│              │  coupler│                │
│              └─────────┘                │
└─────────────────────────────────────────┘
         Side view: 3D-integrated transceiver
```

### Assembly Flow

| Step | Process | Tool |
|------|---------|------|
| 1 | Photonic die dicing + facet polish | Dicing saw + ion polish |
| 2 | CMOS wafer thinning (50 μm) | Grinder + CMP |
| 3 | TSV etch + fill (photonic side) | DRIE + Cu plating |
| 4 | μbump formation | Electroplating + reflow |
| 5 | Flip-chip bond | Thermocompression bonder |
| 6 | Underfill + cure | Capillary dispense |
| 7 | Fiber attach / lens align | Active alignment station |
| 8 | Hermetic seal | Seam weld or lid attach |
| 9 | Burn-in test | 85°C, 168 hr, full optical test |

---

## Radiation Hardening

| Threat | Effect | Mitigation |
|--------|--------|------------|
| Total ionizing dose (TID) | Darkening in SiO₂, index shift | Rad-hard cladding, anneal cycles |
| Displacement damage (DD) | Waveguide loss increase | Si₃N₄ > TFLN in tolerance |
| Single event upset (SEU) | CMOS state flip | Triple-modular redundancy, EDAC |
| Single event latchup (SEL) | CMOS destructive current | SOI CMOS, current limits |

**Testing protocol:**
- Co-60 gamma for TID (up to 100 krad(Si))
- Proton beam for DD (up to 10¹² p/cm², 50 MeV)
- Laser microbeam for SEU/SEL mapping

---

## Foundry Partners & Capacity

| Partner | Location | Capability | Status |
|---------|----------|------------|--------|
| 图灵量子 (TuringQ) | Shanghai | TFLN MPW, 200 mm | Active, pilot line |
| 中科院微电子所 | Beijing | Si₃N₄ PDK, 300 mm | Available |
| 宁波大学 (partner lab) | Ningbo | Chalcogenide growth, custom | R&D scale |
| 哈工大 (HIT) | Harbin | Space qualification, test | Collaboration |
| 三安光电 | Xiamen | InP/Si photonics, foundry | Potential |

---

## Manufacturing Roadmap

| Year | Milestone | Output |
|------|-----------|--------|
| 2026 | TFLN PDK v1.0 (TuringQ) | MPW runs, test devices |
| 2027 | Si₃N₄ + TFLN integration demo | 2-layer wafer, functioning OPA |
| 2028 | Chalcogenide switch module | Packaged device, FWM demo |
| 2029 | Hybrid photonic-CMOS transceiver | Engineering model, rad test |
| 2030 | Space-qualified flight model | TRL 6, qualification complete |
| 2031 | Production scale | 1000 units/year capacity |

---

## Cost Model (Target)

| Item | Unit Cost @ 1000 units | Driver |
|------|----------------------|--------|
| TFLN-Si₃N₄ wafer (200 mm) | $2,000–3,000 | LiNbO₃ substrate, bonding yield |
| Chalcogenide switch chip | $500–800 | Deposition time, Ag doping control |
| CMOS control die | $200–400 | Node: 22 nm FD-SOI |
| 3D assembly + test | $1,000–1,500 | Alignment time, hermeticity |
| **Total transceiver module** | **$4,000–6,000** | — |
| Full satellite photonic payload | $50,000–100,000 | 10–20 modules + structure |

---

## Related Documents

- `vleo_mega_constellation.md` — System architecture using these devices
- `constellation_tracking.md` — Application: hypersonic tracking
- `SPACE_PHOTONICS.md` — Material properties, references, partner list

---

*Last updated: 2026-08-15*
