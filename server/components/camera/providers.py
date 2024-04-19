from server.providers import ServiceProvider
from server.webserver.route import Route

from .api_handlers import APIHandler
from .constants import CHANNEL_CAMERA_CAPTURE_PREVIEW


class ComponentServiceProvider(ServiceProvider):
    """The component service provider."""

    channels = [CHANNEL_CAMERA_CAPTURE_PREVIEW]

    routes = [
        Route.post("/api/v0/camera/capture", APIHandler, "capture"),
    ]
