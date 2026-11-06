"""Typed Python client for the Beaconless telemetry API.

Docs: https://beaconless-api.pages.dev/api-reference
"""
from .client import Client, BeaconlessError

__all__ = ["Client", "BeaconlessError"]
__version__ = "0.1.0"
