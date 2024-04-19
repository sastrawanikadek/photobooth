from http import HTTPStatus

from aiohttp import web

from server.utils.supports.http_response import HTTPResponse

from ..exceptions import WebSocketCommandNotFoundError
from ..models import (
    WebSocketErrorEnvelope,
    WebSocketIncomingMessage,
    WebSocketResponseMessage,
)


def http_not_found_error_renderer(
    exception: web.HTTPNotFound,
    _: web.Request,
) -> web.StreamResponse:
    return HTTPResponse.error(
        message=str(exception) or "Page Not Found",
        status=HTTPStatus.NOT_FOUND,
    )


def websocket_command_not_found_error_renderer(
    exception: WebSocketCommandNotFoundError,
    _: web.WebSocketResponse,
    message: WebSocketIncomingMessage,
) -> WebSocketResponseMessage:
    return WebSocketResponseMessage(
        status="error",
        command=message.command,
        error=WebSocketErrorEnvelope(
            message=str(exception) or "Unknown Command",
        ),
    )
