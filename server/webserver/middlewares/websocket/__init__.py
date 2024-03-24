"""Collection of WebSocket middlewares."""

from ..interfaces import WebSocketMiddlewareInterface
from .exception_handler import ExceptionHandlerMiddleware

DEFAULT_MIDDLEWARES: list[
    type[WebSocketMiddlewareInterface] | WebSocketMiddlewareInterface
] = [ExceptionHandlerMiddleware]

__all__ = ["DEFAULT_MIDDLEWARES"]
