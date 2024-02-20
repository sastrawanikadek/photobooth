from server.managers.settings.api_handlers import APIHandler as SettingsAPIHandler

from .interface import ServiceProviderInterface


class WebSocketRoutesServiceProvider(ServiceProviderInterface):
    """The WebSocket routes service provider."""

    websocket_routes = [
        ("settings.getAll", SettingsAPIHandler, "get_all"),
    ]
