# Constellation Tracking Architecture

> VLEO satellite constellation for hypersonic vehicle tracking & guidance.

## System Overview

### Orbit Parameters
| Parameter | Value |
|-----------|-------|
| Altitude | ~200–400 km (VLEO) |
| Inclination | [TBD] |
| Number of satellites | [TBD] |
| Revisit time target | [TBD] |

### Optical Payload
- **Transmit:** Multi-face OPA for agile beam steering
- **Receive:** [TBD — SPAD array? Coherent?]
- **Wavelength:** [TBD — 1550 nm atmospheric window? 1064 nm?]
- **Link budget margin:** [TBD]

### Onboard Processing
- **Photonic accelerator:** Ag-chalcogenide for all-optical matrix-vector multiplication
- **Hybrid control loop:** Optical inner loop (ns) + EO outer loop (μs)

## Tracking Strategy

### Phase 1: Acquisition
- Wide-angle beacon from hypersonic vehicle (or ground uplink)
- OPA broad scan pattern

### Phase 2: Tracking
- Nested control loops:
  - Inner: All-optical phase-locked loop (Kerr-based? FWM-based?)
  - Outer: Digital Kalman filter predicting vehicle trajectory

### Phase 3: Guidance Handoff
- [TBD]

## Open Questions

1. Atmospheric turbulence compensation: AO vs. modal vs. scintillation diversity?
2. Point-ahead angle for hypersonic velocities (Mach 5+)?
3. Thermal management at VLEO (atomic oxygen, drag, heating)?

---

*Created: 2026-08-13*
