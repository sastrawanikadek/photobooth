from aiohttp import web

from ..models import (
    WebSocketErrorEnvelope,
    WebSocketIncomingMessage,
    WebSocketResponseMessage,
)


def websocket_value_error_renderer(
    exception: ValueError, _: web.WebSocketResponse, message: WebSocketIncomingMessage
) -> WebSocketResponseMessage:
    return WebSocketResponseMessage(
        status="error",
        command=message.command,
        error=WebSocketErrorEnvelope(
            message=str(exception),
        ),
    )
