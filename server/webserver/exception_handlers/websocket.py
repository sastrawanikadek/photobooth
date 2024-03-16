import inspect
from typing import Callable, TypeVar, cast

from aiohttp import web
from pydantic import ValidationError

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

    def register(self) -> None:
        """Register exceptions to the handler."""
        self.render(ValueErrorRenderer)
        self.render(ValidationErrorRenderer)

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


def ValueErrorRenderer(
    exception: ValueError, _: web.WebSocketResponse, message: WebSocketIncomingMessage
) -> WebSocketResponseMessage:
    return WebSocketResponseMessage(
        status="error",
        command=message.command,
        error=WebSocketErrorEnvelope(
            message=str(exception),
        ),
    )


def ValidationErrorRenderer(
    exception: ValidationError,
    _: web.WebSocketResponse,
    message: WebSocketIncomingMessage,
) -> WebSocketResponseMessage:
    errors: dict[str, list[str]] = {}

    for error in exception.errors():
        field = ".".join([str(v) for v in error["loc"]])
        errors.setdefault(field, [])
        errors[field].append(error["msg"])

    return WebSocketResponseMessage(
        status="error",
        command=message.command,
        error=WebSocketErrorEnvelope(
            message="Validation Error",
            errors=errors,
        ),
    )
