from aiohttp import web

from ...exception_handlers import (
    WebSocketExceptionHandler,
    WebSocketValidationErrorRenderer,
    WebSocketValueErrorRenderer,
)
from ...models import WebSocketIncomingMessage, WebSocketResponseMessage
from ..interfaces import WebSocketMiddlewareHandler, WebSocketMiddlewareInterface


class ExceptionHandlerMiddleware(WebSocketMiddlewareInterface):
    """Middleware to handle exceptions."""

    def __init__(self, handler: WebSocketExceptionHandler) -> None:
        """Initialize the middleware."""
        self.handler = handler

        self.handler.render(WebSocketValidationErrorRenderer)
        self.handler.render(WebSocketValueErrorRenderer)

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
