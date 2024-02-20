from server.providers import ServiceProviderInterface

from .api_handlers import APIHandler


class WebSocketRoutesServiceProvider(ServiceProviderInterface):
    """The WebSocket routes service provider."""

    websocket_routes = [
        ("camera.capturePreview", APIHandler, "capture_preview"),
        ("camera.capture", APIHandler, "capture"),
    ]
