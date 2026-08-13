#!/usr/bin/env python3
"""Quick test of the digital twin with fast settings."""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/space-photonics/twin')

from twin import DigitalTwin, TwinConfig

print("Testing Space Photonics Digital Twin...")
print("=" * 50)

# Test 1: Basic initialization
print("\n1. Initializing with default config...")
config = TwinConfig(dt=1e-4)  # Larger dt for faster test
twin = DigitalTwin(config)
print("   ✓ Initialized successfully")

# Test 2: Run short simulation
print("\n2. Running 0.01 second simulation...")
twin.run(duration=0.01)
print("   ✓ Simulation complete")

# Test 3: Summary
print("\n3. Results:")
summary = twin.get_summary()
for key, val in summary.items():
    if isinstance(val, float):
        print(f"   {key}: {val:.4f}")
    else:
        print(f"   {key}: {val}")

print("\n" + "=" * 50)
print("All tests passed! The digital twin is ready.")
