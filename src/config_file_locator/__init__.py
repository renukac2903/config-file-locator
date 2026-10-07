"""Config File Locator: search upward from a starting path for a named config file."""

from .core import find_config, locate_config, ConfigNotFoundError

__all__ = ["find_config", "locate_config", "ConfigNotFoundError"]
