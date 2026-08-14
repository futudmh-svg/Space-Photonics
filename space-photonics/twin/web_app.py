"""
Streamlit Web App for Space Photonics Digital Twin

Run with: streamlit run web_app.py

This creates a mobile-friendly web interface where you can:
- Run simulations with adjustable parameters
- View real-time plots
- Compare TFLN vs BTO performance
- No coding required — just sliders and buttons
"""

import sys
import os

# Try multiple paths to find the twin module
possible_paths = [
    os.path.join(os.path.dirname(__file__), '.'),  # Same dir as web_app.py
    '/mount/src/space-photonics/space-photonics/twin',  # Streamlit Cloud
    '/root/.openclaw/workspace/space-photonics/twin',  # Local dev
]

for path in possible_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        break

import numpy as np
import matplotlib.pyplot as plt
from twin import DigitalTwin, TwinConfig, get_scenario
from twin.bto_phase_shifter import compare_tfln_vs_bto

try:
    import streamlit as st
except ImportError:
    print("Streamlit not installed. Install with: pip install streamlit")
    print("Then run: streamlit run web_app.py")
    sys.exit(1)

# Page config
st.set_page_config(
    page_title="Space Photonics Digital Twin",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile
st.markdown("""
<style>
    .stButton>button { width: 100%; }
    .stSlider { padding-top: 10px; padding-bottom: 10px; }
    @media (max-width: 768px) {
        .stMarkdown { font-size: 14px; }
    }
</style>
""", unsafe_allow_html=True)

st.title("🛰️ Space Photonics Digital Twin")
st.markdown("*VLEO Satellite-to-Hypersonic Vehicle Optical Link Simulator*")

# Tabs
tab1, tab2, tab3 = st.tabs(["🎮 Run Simulation", "📊 Results", "⚖️ TFLN vs BTO"])

with tab1:
    st.header("Simulation Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scenario = st.selectbox(
            "Scenario",
            ["tracking", "acquisition", "thermal_stress", "default", "fast"],
            index=0
        )
        duration = st.slider("Duration (seconds)", 0.01, 10.0, 1.0, 0.1)
        
    with col2:
        tx_power = st.slider("TX Power (W)", 0.1, 10.0, 1.0, 0.1)
        wavelength = st.selectbox("Wavelength", ["1550 nm", "1064 nm", "780 nm"], index=0)
    
    # Convert wavelength
    wl_map = {"1550 nm": 1550e-9, "1064 nm": 1064e-9, "780 nm": 780e-9}
    wl = wl_map[wavelength]
    
    # Subsystem toggles
    st.subheader("Subsystems")
    col3, col4, col5 = st.columns(3)
    with col3:
        enable_tracking = st.toggle("Tracking", True)
    with col4:
        enable_thermal = st.toggle("Thermal", True)
    with col5:
        enable_nested = st.toggle("Nested Control", True)
    
    # Run button
    if st.button("🚀 Run Simulation", type="primary"):
        with st.spinner("Running simulation..."):
            config = get_scenario(scenario)
            config.duration = duration
            config.tx_power = tx_power
            config.wavelength = wl
            config.enable_tracking = enable_tracking
            config.enable_thermal = enable_thermal
            config.enable_nested_control = enable_nested
            
            twin = DigitalTwin(config)
            twin.run(duration=duration)
            
            # Store in session state
            st.session_state.twin = twin
            st.session_state.summary = twin.get_summary()
            st.session_state.log_data = twin.log_data
            
        st.success("Simulation complete! Go to Results tab.")

with tab2:
    st.header("Simulation Results")
    
    if 'twin' not in st.session_state:
        st.info("Run a simulation first in the 'Run Simulation' tab.")
    else:
        summary = st.session_state.summary
        data = st.session_state.log_data
        
        # Summary cards
        st.subheader("Summary")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Mean SNR", f"{summary.get('mean_snr_db', 0):.1f} dB")
        with c2:
            st.metric("RX Power", f"{summary.get('mean_rx_power_dbm', 0):.1f} dBm")
        with c3:
            st.metric("Duration", f"{summary.get('duration', 0):.3f} s")
        with c4:
            st.metric("Pointing Error", f"{summary.get('final_pointing_error', 0):.4f}°")
        
        # Plots
        if data:
            times = [d['time'] for d in data]
            snrs = [d['optical']['snr_db'] for d in data]
            rx_powers = [d['optical']['rx_power_dbm'] for d in data]
            
            st.subheader("SNR Over Time")
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.plot(times, snrs, 'b-', linewidth=1)
            ax1.set_xlabel('Time [s]')
            ax1.set_ylabel('SNR [dB]')
            ax1.grid(True, alpha=0.3)
            st.pyplot(fig1)
            
            st.subheader("Received Power")
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(times, rx_powers, 'g-', linewidth=1)
            ax2.set_xlabel('Time [s]')
            ax2.set_ylabel('RX Power [dBm]')
            ax2.grid(True, alpha=0.3)
            st.pyplot(fig2)
            
            # JSON export
            st.subheader("Export")
            import json
            json_str = json.dumps(data, indent=2)
            st.download_button(
                "Download JSON",
                json_str,
                file_name="simulation_results.json",
                mime="application/json"
            )

with tab3:
    st.header("TFLN vs BTO Phase Shifter Comparison")
    
    st.markdown("""
    **TFLN (Lithium Niobate)** — Mature, commercial PDKs available
    - Drive voltage: ~20 V (thermal tuning)
    - Switching: ~1-10 μs
    - Power: ~10 mW per heater
    
    **BTO (Barium Titanate)** — Research stage, 5-10 years from commercial PDK
    - Drive voltage: ~7.5 V (electro-optic)
    - Switching: ~50 ps
    - Power: ~μW (capacitive only)
    """)
    
    if st.button("Compare Performance"):
        with st.spinner("Running comparison..."):
            # Capture print output
            import io
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                compare_tfln_vs_bto()
            except Exception as e:
                st.error(f"Error: {e}")
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
        st.text(output)
        
        # Visual comparison
        st.subheader("Drive Voltage Comparison")
        fig, ax = plt.subplots(figsize=(8, 4))
        materials = ['TFLN', 'BTO']
        voltages = [20, 7.5]
        colors = ['#FF6B6B', '#4ECDC4']
        ax.bar(materials, voltages, color=colors)
        ax.set_ylabel('Vπ [V]')
        ax.set_title('Phase Shifter Drive Voltage (lower is better)')
        for i, v in enumerate(voltages):
            ax.text(i, v + 0.5, f'{v} V', ha='center', fontweight='bold')
        st.pyplot(fig)
        
        st.subheader("Switching Speed")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        speeds = [10000, 0.05]  # ns
        ax2.bar(materials, speeds, color=colors)
        ax2.set_ylabel('Switching Time [ns]')
        ax2.set_title('Switching Speed (lower is better)')
        ax2.set_yscale('log')
        for i, s in enumerate(speeds):
            label = f'{s*1000:.0f} ps' if s < 1 else f'{s:.0f} ns'
            ax2.text(i, s * 1.5, label, ha='center', fontweight='bold')
        st.pyplot(fig2)

# Footer
st.markdown("---")
st.markdown("📱 *Optimized for mobile | [GitHub Repo](https://github.com/futudmh-svg/Space-Photonics)*")
