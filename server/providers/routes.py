from server.managers.settings.api_handlers import (
    HTTPAPIHandler as SettingsHTTPAPIHandler,
)
from server.webserver.api_handlers import (
    WebSocketAPIHandler as WebServerWebSocketAPIHandler,
)
from server.webserver.route import Route

from .base import ServiceProvider


class RoutesServiceProvider(ServiceProvider):
    """The API routes service provider."""

    routes = [
        Route.get(
            "/api/v0/settings",
            SettingsHTTPAPIHandler,
            "get_all",
        ),
        Route.put(
            "/api/v0/settings/{uuid}",
            SettingsHTTPAPIHandler,
            "update",
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
