from aiohttp import web

from ...exception_handlers import (
    WebSocketExceptionHandler,
    websocket_command_not_found_error_renderer,
    websocket_validation_error_renderer,
    websocket_value_error_renderer,
)
from ...models import WebSocketIncomingMessage, WebSocketResponseMessage
from ..interfaces import WebSocketMiddlewareHandler, WebSocketMiddlewareInterface


class ExceptionHandlerMiddleware(WebSocketMiddlewareInterface):
    """Middleware to handle exceptions."""

    def __init__(self, handler: WebSocketExceptionHandler) -> None:
        """Initialize the middleware."""
        self.handler = handler

        self.handler.render(websocket_validation_error_renderer)
        self.handler.render(websocket_value_error_renderer)
        self.handler.render(websocket_command_not_found_error_renderer)

    async def handle(
        self,
        connection: web.WebSocketResponse,
        message: WebSocketIncomingMessage,
        handler: WebSocketMiddlewareHandler,
    ) -> WebSocketResponseMessage:
        """Handle the request."""
        try:
            response = await handler(connection, message)
        except Exception as exception:
            response = self.handler.handle(exception, connection, message)

        return response
