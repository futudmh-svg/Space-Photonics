# Space Photonics Digital Twin 🛰️

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=futudmh-svg/Space-Photonics)
[![Run on Replit](https://replit.com/badge/github/futudmh-svg/Space-Photonics)](https://replit.com/github/futudmh-svg/Space-Photonics)

All-optical digital twin for VLEO satellite-to-hypersonic vehicle optical communication.

---

## 📱 Run on Your Phone (No Installation)

### Option 1: Streamlit Web App (Easiest — Just a Browser)

**Coming soon** — Deploy to Streamlit Cloud for one-click access. For now:

1. Open [GitHub Codespaces](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=futudmh-svg/Space-Photonics)
2. In the terminal, run:
   ```bash
   cd Space-Photonics
   pip install streamlit
   streamlit run space-photonics/twin/web_app.py
   ```
3. Click the forwarded port link (port 8501) — works on mobile!

### Option 2: Replit (Mobile-Friendly IDE)

1. Go to **https://replit.com/github/futudmh-svg/Space-Photonics**
2. Click **Import from GitHub**
3. Click the **Run** button — works great on phone browsers

### Option 3: Binder (Launch Jupyter in Browser)

1. Go to **https://mybinder.org/v2/gh/futudmh-svg/Space-Photonics/main**
2. Wait ~2 minutes for the environment to build
3. Open `space-photonics/twin/twin_demo.ipynb`
4. Run cells with the ▶️ button

### Option 4: Google Colab

1. Go to **https://colab.research.google.com/**
2. File → Upload Notebook → Choose `space-photonics/twin/twin_demo.ipynb`
3. Run all cells (Ctrl+F9 or tap the play buttons)

---

## 🖥️ Run Locally

```bash
git clone https://github.com/futudmh-svg/Space-Photonics.git
cd Space-Photonics/space-photonics/twin
pip install -e .
python3 -m twin --scenario tracking --duration 10.0
```

---

## What's Inside

| Technology | Status | Notes |
|-----------|--------|-------|
| TFLN OPA Phase Shifters | ✅ | Mature, thermal tuning |
| **BTO Phase Shifters** | ✅ **New** | 30x lower voltage, ps switching |
| Ag-Chalcogenide Amplifier | ✅ | All-optical gain |
| Nested Control (Optical PLL + Kalman) | ✅ | ns + μs loops |
| Atmospheric Channel | ✅ | Turbulence, scintillation |
| VLEO Thermal Model | ✅ | Atomic oxygen, aerothermal |
| **Streamlit Web App** | ✅ **New** | Phone-optimized UI |

## Repository Structure

```
Space-Photonics/
├── space-photonics/
│   ├── twin/                 # Digital twin package
│   │   ├── web_app.py        # 📱 Streamlit mobile app
│   │   ├── demo.py           # Quick demo
│   │   └── ...
│   ├── architecture/         # System architecture docs
│   └── calculations/         # Standalone link budget
├── .devcontainer/            # Codespaces config
├── .replit                   # Replit config
└── requirements.txt          # Python dependencies
```

## Documentation

- [Twin Tutorial](space-photonics/twin/TUTORIAL.md) — Step-by-step guide
- [Changelog](space-photonics/twin/CHANGELOG.md) — Release history

## License

MIT
