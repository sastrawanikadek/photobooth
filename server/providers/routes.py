from server.managers.settings import HTTPAPIHandler as SettingsHTTPAPIHandler
from server.webserver import Route
from server.webserver import WebSocketAPIHandler as WebServerWebSocketAPIHandler

from .base import ServiceProvider


class RoutesServiceProvider(ServiceProvider):
    """The API routes service provider."""

    routes = [
        Route.get(
            "/api/v0/settings",
            SettingsHTTPAPIHandler,
            "get_all",
        ),
        Route.websocket(
            "subscribe",
            WebServerWebSocketAPIHandler,
            "subscribe",
        ),
        Route.websocket(
            "unsubscribe",
            WebServerWebSocketAPIHandler,
            "unsubscribe",
        ),
    ]
