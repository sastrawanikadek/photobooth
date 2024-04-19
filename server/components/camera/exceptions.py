from http import HTTPStatus

from aiohttp import web

from server.utils.supports.http_response import HTTPResponse
from server.utils.supports.websocket_response import WebSocketResponse
from server.webserver.models import WebSocketIncomingMessage, WebSocketResponseMessage


class CameraError(Exception):
    """Base class for camera errors."""

    def http_render(self, _: web.Request) -> web.StreamResponse:
        """Render the error to an HTTP response."""
        return HTTPResponse.error(message=str(self), status=HTTPStatus.BAD_GATEWAY)

    def websocket_render(
        self, _: web.WebSocketResponse, message: WebSocketIncomingMessage
    ) -> WebSocketResponseMessage:
        """Render the error to a WebSocket response."""
        return WebSocketResponse.error(message=str(self))


class ModelNotFoundError(CameraError):
    """Raised when the specified camera model is not found."""


class DeviceUSBNotFoundError(CameraError):
    """Raised when the camera is not connected to USB port."""
