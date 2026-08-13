"""
Space Photonics Digital Twin - Core Simulation Framework

Modules:
    opa_beamsteer    - Multi-face OPA beam steering model
    agchalcogenide   - Ag-doped chalcogenide amplifier dynamics  
    orbit_target     - VLEO orbit + hypersonic vehicle propagator
    twin_orchestrator - Main simulation orchestrator
    visualize        - Result visualization utilities

Usage:
    from space_photonics_twin import DigitalTwin, TwinConfig
    twin = DigitalTwin(config)
    twin.run(duration=10.0, dt=1e-6)
"""

from .twin_orchestrator import DigitalTwin, TwinConfig
from .opa_beamsteer import OPABeamSteerer, OPAConfig
from .agchalcogenide import AgChalcogenideAmplifier, AgChalcogenideConfig
from .orbit_target import VLEOPropagator, HypersonicVehicle, OrbitConfig, VehicleConfig

__version__ = "0.1.0"
__author__ = "Space Photonics Team"
