"""
Application configuration module.

Centralizes environment-driven settings and runtime configuration values.
Feature-specific configuration should extend patterns defined here.
"""

from pathlib import Path


class AppConfig(object):
    """Immutable application configuration container."""

    def __init__(self):
        self.app_name = "Kosvio"
        self.debug = False
        self.base_dir = Path(__file__).resolve().parent


def get_config():
    """
    Build and return the active application configuration.

    Returns:
        AppConfig: Resolved configuration for the current runtime.
    """
    return AppConfig()
