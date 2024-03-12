"""Module for managing service providers for the application."""

from .app import AppServiceProvider
from .base import ServiceProvider
from .routes import RoutesServiceProvider
from .settings import SettingsServiceProvider

DEFAULT_PROVIDERS = [
    AppServiceProvider,
    SettingsServiceProvider,
    RoutesServiceProvider,
]

__all__ = ["ServiceProvider", "DEFAULT_PROVIDERS"]
