# Space Photonics — Full Audit & Contradiction Report

## Critical Contradictions Found

### 1. SATELLITE ALTITUDE — MAJOR CONTRADICTION
- **architecture.html**: "VLEO satellite (250 km)"
- **vleo-constellation.html**: "h = 300 km" (multiple places)
- **hypersonic.html**: Slider default was 250 km (now fixed to 300)
- **FIXED**: Standardized to 300 km everywhere

### 2. CHALCOGENIDE vs PPLN
- **architecture.html line 302**: Still lists "Ag-doped As₂S₃" in a table
- **research-gaps.html**: Correctly notes this was replaced
- **vleo-constellation.html**: Correctly uses PPLN
- **FIX**: Remove chalcogenide from architecture.html table

### 3. DOPPLER SHIFT CALCULATION
- **vleo-constellation.html**: "Δf = 193.5×10¹² × 3430 / 3×10⁸ = 2.21 GHz"
- **Verification**: f = c/λ = 3×10⁸ / 1550×10⁻⁹ = 193.5 THz ✓
- **Δf/f = v/c**: 3430 / 3×10⁸ = 1.14×10⁻⁵
- **Δf = 193.5×10¹² × 1.14×10⁻⁵ = 2.21×10⁹ Hz = 2.21 GHz** ✓ CORRECT

### 4. PLASMA FREQUENCY
- **vleo-constellation.html**: "ω_p = 9√n_e [Hz] with n_e in m⁻³"
- For n_e = 10¹⁸: ω_p = 9×10⁹ Hz = 9 GHz ✓
- For n_e = 10¹⁹: ω_p = 28×10⁹ Hz = 28 GHz ✓
- **Optical carrier at 193.5 THz >> plasma frequency** ✓ CORRECT

### 5. ORBITAL PERIOD
- **vleo-constellation.html**: T = 2π√((6371+300)³×10⁹/3.986×10¹⁴) = 5431 s = 90.5 min ✓
- **Verification**: a = 6671 km = 6.671×10⁶ m
- T = 2π√(a³/μ) = 2π√(2.97×10²⁰/3.986×10¹⁴) = 2π√(7.45×10⁵) = 2π×863 = 5423 s ✓

### 6. LINK BUDGET — NEEDS VERIFICATION
- Architecture page claims: RX Power = -55 dBm, SNR = 28 dB, Margin = 10 dB
- These numbers need to be derived from first principles
- **ACTION**: Add interactive calculator to link-budget.html

### 7. PPLN EFFICIENCY
- Architecture page: "PPLN Eff. 2000%/W" — this is unclear
- **ACTION**: Clarify this is parametric gain efficiency, not quantum efficiency

## Hallucinations / Unverified Claims

1. "1 cm accuracy achievable" for auto-tracking — needs citation
2. "28 dB SNR" — needs full link budget derivation
3. "-65 dBm min detectable" — needs PPLN conversion efficiency justification
4. "150 satellites feasible (Starlink flies 7000+)" — Starlink is at 550 km, not 300 km

## Visual Issues

1. **index.html**: 3D hero may have aspect ratio issues on mobile
2. **hypersonic.html**: New 3D sim added but may conflict with existing canvas
3. **opa-analysis.html**: 3D beam steering partially implemented
4. **link-budget.html**: No interactive calculator yet

## Navigation Issues

- All pages now have consistent 15-link nav bars ✓ (fixed by update_nav3.py)
- foundry-cleanroom.html has relative links without ../ (correct for its location)

## Git Status

- Token configured: github_pat_11CLNF6PQ0... (truncated)
- Branch: main
- Need to commit all fixes and push
