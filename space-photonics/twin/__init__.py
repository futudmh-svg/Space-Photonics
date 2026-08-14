"""
Space Photonics Digital Twin - Core Simulation Framework

Modules:
    opa_beamsteer      - Multi-face OPA beam steering with TFLN phase shifters
    agchalcogenide     - Ag-doped chalcogenide all-optical amplifier
    orbit_target       - VLEO orbit + hypersonic vehicle propagator
    control_loop       - Nested optical PLL + digital Kalman tracker
    atmospheric_channel - Turbulence, scintillation, beam wander
    thermal_model      - VLEO thermal environment + atomic oxygen heating
    twin_orchestrator  - Main simulation controller
    visualize          - Result plotting utilities
    config_manager     - Configuration management
    parameter_sweep    - Design of experiments

Usage:
    from space_photonics_twin import DigitalTwin, TwinConfig
    twin = DigitalTwin(config)
    twin.run(duration=10.0)
"""

from .twin_orchestrator import DigitalTwin, TwinConfig
from .opa_beamsteer import OPABeamSteerer, OPAConfig
from .agchalcogenide import AgChalcogenideAmplifier, AgChalcogenideConfig
from .orbit_target import VLEOPropagator, HypersonicVehicle, OrbitConfig, VehicleConfig
from .control_loop import NestedControlSystem, OpticalPhaseLockedLoop, DigitalKalmanTracker
from .atmospheric_channel import AtmosphericChannel, AtmosphericConfig
from .thermal_model import VLEOThermalModel, VLEOThermalConfig
from .bto_phase_shifter import (
    BTOPhaseShifter, BTOPhaseShifterConfig,
    BTOOPA, BTOOPAConfig
)
from .config_manager import (
    load_config, save_config, get_default_config,
    get_high_performance_config, get_fast_config,
    get_scenario, list_scenarios
)

__version__ = "0.2.0"
__author__ = "Space Photonics Team"
