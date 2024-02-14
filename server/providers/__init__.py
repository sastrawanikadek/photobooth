"""Module for managing service providers for the application."""

from .app import AppServiceProvider
from .interface import ServiceProviderInterface
from .settings import SettingsServiceProvider
from .websocket_routes import WebSocketRoutesServiceProvider

DEFAULT_PROVIDERS = [
    AppServiceProvider,
    SettingsServiceProvider,
    WebSocketRoutesServiceProvider,
]

__all__ = ["ServiceProviderInterface", "DEFAULT_PROVIDERS"]
