#!/usr/bin/env python3
"""Generate demo plots to show user output directly."""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/space-photonics')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from twin import DigitalTwin, TwinConfig, get_scenario
from twin.opa_beamsteer import OPABeamSteerer, OPAConfig
from twin.atmospheric_channel import AtmosphericChannel, AtmosphericConfig

print("Running Space Photonics Digital Twin...")
print("=" * 50)

# 1. Run simulation
config = get_scenario('tracking')
config.dt = 1e-4
config.log_interval = 1e-2
twin = DigitalTwin(config)
twin.run(duration=0.1)
summary = twin.get_summary()

print("\nSimulation Complete!")
print(f"  Duration: {summary['duration']:.3f} s")
print(f"  Mean SNR: {summary['mean_snr_db']:.1f} dB")
print(f"  Mean RX Power: {summary['mean_rx_power_dbm']:.1f} dBm")

# 2. Plot 1: SNR and Power
data = twin.log_data
times = [d['time'] for d in data]
snrs = [d['optical']['snr_db'] for d in data]
rx_power = [d['optical']['rx_power_dbm'] for d in data]
pointing = [d['optical']['pointing_error'] for d in data]

fig, axes = plt.subplots(3, 1, figsize=(10, 8))
axes[0].plot(times, snrs, 'b-', linewidth=1)
axes[0].set_ylabel('SNR [dB]')
axes[0].set_title('Optical Link Performance (0.1s simulation)')
axes[0].grid(True, alpha=0.3)

axes[1].plot(times, rx_power, 'g-', linewidth=1)
axes[1].set_ylabel('RX Power [dBm]')
axes[1].grid(True, alpha=0.3)

axes[2].plot(times, pointing, 'r-', linewidth=1)
axes[2].set_ylabel('Pointing Error [deg]')
axes[2].set_xlabel('Time [s]')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/plot1_simulation.png', dpi=150)
print("  Saved: plot1_simulation.png")

# 3. Plot 2: OPA Far-Field
opa = OPABeamSteerer(OPAConfig(wavelength=1550e-9, num_elements=64))
opa.set_steering_angle(15.0)
theta_range = np.linspace(-30, 30, 500)
intensity = opa.compute_farfield(np.radians(theta_range))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(theta_range, 10*np.log10(intensity + 1e-10), 'b-', linewidth=1)
ax.set_xlabel('Angle [deg]')
ax.set_ylabel('Intensity [dB]')
ax.set_title('OPA Far-Field Pattern (64 elements, steered to 15°)')
ax.set_ylim([-60, 5])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/plot2_opa.png', dpi=150)
print("  Saved: plot2_opa.png")

# 4. Plot 3: Atmospheric Seeing
atm = AtmosphericChannel(AtmosphericConfig())
r0_values = [atm.compute_r0(el) for el in range(5, 91, 5)]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(range(5, 91, 5), r0_values, 'ro-', markersize=4)
ax.set_xlabel('Elevation [deg]')
ax.set_ylabel('Fried Parameter r0 [m]')
ax.set_title('Atmospheric Seeing vs Elevation')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/plot3_atmosphere.png', dpi=150)
print("  Saved: plot3_atmosphere.png")

print("\n" + "=" * 50)
print("All plots generated successfully!")
