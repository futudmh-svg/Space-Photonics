"""
Configuration Management

Load/save simulation configurations from JSON/YAML files.
"""

import json
from pathlib import Path
from typing import Union, Dict
from dataclasses import asdict

from .twin_orchestrator import TwinConfig


def load_config(filepath: Union[str, Path]) -> TwinConfig:
    """
    Load configuration from JSON file.
    
    Args:
        filepath: Path to JSON config file
        
    Returns:
        TwinConfig instance
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return TwinConfig(**data)


def save_config(config: TwinConfig, filepath: Union[str, Path]):
    """
    Save configuration to JSON file.
    
    Args:
        config: TwinConfig instance
        filepath: Path to save JSON
    """
    with open(filepath, 'w') as f:
        json.dump(asdict(config), f, indent=2)


def get_default_config() -> TwinConfig:
    """Get default simulation configuration."""
    return TwinConfig()


def get_high_performance_config() -> TwinConfig:
    """Get high-performance configuration (more accurate, slower)."""
    return TwinConfig(
        dt=1e-7,              # 100 ns timestep
        log_interval=1e-4,     # 100 us logging
        tx_power=2.0,
        tx_aperture=0.2,
        rx_aperture=0.1,
        enable_nested_control=True,
        enable_thermal=True
    )


def get_fast_config() -> TwinConfig:
    """Get fast configuration (less accurate, faster)."""
    return TwinConfig(
        dt=1e-5,              # 10 us timestep
        log_interval=1e-2,     # 10 ms logging
        enable_nested_control=False,
        enable_thermal=False
    )


# Example configurations
SCENARIOS = {
    'default': get_default_config(),
    'high_performance': get_high_performance_config(),
    'fast': get_fast_config(),
    'acquisition': TwinConfig(
        enable_tracking=False,  # Wide scan
        pointing_loss_db=10.0   # Higher initial loss
    ),
    'tracking': TwinConfig(
        enable_tracking=True,
        enable_nested_control=True,
        tracking_bandwidth=10e3
    ),
    'thermal_stress': TwinConfig(
        enable_thermal=True,
        atmospheric_loss_db=5.0  # Worse weather
    )
}


def list_scenarios() -> list:
    """List available scenario names."""
    return list(SCENARIOS.keys())


def get_scenario(name: str) -> TwinConfig:
    """
    Get predefined scenario configuration.
    
    Args:
        name: Scenario name
        
    Returns:
        TwinConfig for scenario
    """
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}. Available: {list_scenarios()}")
    return SCENARIOS[name]
