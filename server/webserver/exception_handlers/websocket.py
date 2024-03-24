import inspect
from typing import Callable, TypeVar, cast

from aiohttp import web

from server.utils.helpers.inspect import has_same_signature

from ..models import (
    WebSocketErrorEnvelope,
    WebSocketIncomingMessage,
    WebSocketResponseMessage,
)

ExceptionType = TypeVar("ExceptionType", bound=Exception)
Handler = Callable[
    [Exception, web.WebSocketResponse, WebSocketIncomingMessage],
    WebSocketResponseMessage | None,
]


class WebSocketExceptionHandler:
    """Exception handler for WebSocket connection."""

    _renderers: dict[type[Exception], Handler] = {}

    def render(
        self,
        handler: Callable[
            [ExceptionType, web.WebSocketResponse, WebSocketIncomingMessage],
            WebSocketResponseMessage | None,
        ],
    ) -> None:
        """Register a renderer for the exception."""
        signature = inspect.signature(handler)
        parameters = list(signature.parameters.values())

        exception_type = parameters[0].annotation

        if not issubclass(exception_type, Exception):
            raise TypeError("Invalid arguments")

        self._renderers[exception_type] = cast(Handler, handler)

    def handle(
        self,
        exception: ExceptionType,
        connection: web.WebSocketResponse,
        message: WebSocketIncomingMessage,
    ) -> WebSocketResponseMessage:
        """Handle an exception."""
        if hasattr(exception, "websocket_render") and callable(
            exception.websocket_render
        ):
            same_signature = has_same_signature(
                exception.websocket_render,
                [web.WebSocketResponse, WebSocketIncomingMessage],
                WebSocketResponseMessage,
            )

            if same_signature:
                return cast(
                    WebSocketResponseMessage,
                    exception.websocket_render(connection, message),
                )

        renderer = self._renderers.get(type(exception))

        if renderer is None:
            for exception_cls, handler in self._renderers.items():
                if issubclass(type(exception), exception_cls):
                    renderer = handler
                    break

        response = (
            None if renderer is None else renderer(exception, connection, message)
        )

        if response is None:
            response = WebSocketResponseMessage(
                status="error",
                command=message.command,
                error=WebSocketErrorEnvelope(message="Internal Server Error"),
            )

        return response
