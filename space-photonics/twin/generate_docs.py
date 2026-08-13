"""
Generate API documentation from docstrings.

Usage: python generate_docs.py
Output: api_reference.md
"""

import inspect
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from space_photonics_twin import (
    DigitalTwin, TwinConfig,
    OPABeamSteerer, OPAConfig,
    AgChalcogenideAmplifier, AgChalcogenideConfig,
    VLEOPropagator, HypersonicVehicle,
    NestedControlSystem,
    AtmosphericChannel, AtmosphericConfig,
    VLEOThermalModel, VLEOThermalConfig
)


def document_class(cls, level=2):
    """Generate markdown documentation for a class."""
    lines = []
    
    # Header
    lines.append(f"{'#' * level} {cls.__name__}\n")
    
    # Docstring
    if cls.__doc__:
        lines.append(cls.__doc__.strip())
        lines.append("")
    
    # Methods
    lines.append(f"{'#' * (level + 1)} Methods\n")
    
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith('_'):
            continue
            
        lines.append(f"**{name}**`{inspect.signature(method)}`\n")
        
        if method.__doc__:
            doc = method.__doc__.strip()
            # Indent docstring
            for line in doc.split('\n'):
                lines.append(f"  {line}")
            lines.append("")
    
    return '\n'.join(lines)


def generate_api_reference():
    """Generate full API reference."""
    
    classes = [
        DigitalTwin,
        TwinConfig,
        OPABeamSteerer,
        OPAConfig,
        AgChalcogenideAmplifier,
        AgChalcogenideConfig,
        VLEOPropagator,
        HypersonicVehicle,
        NestedControlSystem,
        AtmosphericChannel,
        AtmosphericConfig,
        VLEOThermalModel,
        VLEOThermalConfig
    ]
    
    lines = [
        "# Space Photonics Digital Twin - API Reference\n",
        "Auto-generated from docstrings.\n",
        "---\n"
    ]
    
    for cls in classes:
        lines.append(document_class(cls))
        lines.append("---\n")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    docs = generate_api_reference()
    
    with open('API_REFERENCE.md', 'w') as f:
        f.write(docs)
    
    print("API reference generated: API_REFERENCE.md")
