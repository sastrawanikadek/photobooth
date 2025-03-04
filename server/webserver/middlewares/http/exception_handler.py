from aiohttp import web

from ...exception_handlers import (
    HTTPExceptionHandler,
    http_forbidden_error_renderer,
    http_not_found_error_renderer,
    http_validation_error_renderer,
)
from ..interfaces import HTTPMiddlewareHandler, HTTPMiddlewareInterface


class ExceptionHandlerMiddleware(HTTPMiddlewareInterface):
    """Middleware to handle exceptions."""

    def __init__(self, handler: HTTPExceptionHandler) -> None:
        """Initialize the middleware."""
        self.handler = handler

        self.handler.render(http_validation_error_renderer)
        self.handler.render(http_not_found_error_renderer)
        self.handler.render(http_forbidden_error_renderer)

    async def handle(
        self, request: web.Request, handler: HTTPMiddlewareHandler
    ) -> web.StreamResponse:
        """Handle the request."""
        try:
            response = await handler(request)
        except Exception as exception:
            response = self.handler.handle(exception, request)

        return response
