#!/usr/bin/env python3
"""Entry point for running as module: python -m space_photonics_twin"""

from .cli import main
import sys

if __name__ == '__main__':
    sys.exit(main())
