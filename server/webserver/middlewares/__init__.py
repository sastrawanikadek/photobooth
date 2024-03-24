"""Middlewares for HTTP and WebSocket communication."""

from .http import DEFAULT_MIDDLEWARES as DEFAULT_HTTP_MIDDLEWARES
from .interfaces import (
    HTTPMiddlewareHandler,
    HTTPMiddlewareInterface,
    WebSocketMiddlewareHandler,
    WebSocketMiddlewareInterface,
    WebSocketMiddlewareType,
)
from .websocket import DEFAULT_MIDDLEWARES as DEFAULT_WEBSOCKET_MIDDLEWARES

__all__ = [
    "HTTPMiddlewareHandler",
    "WebSocketMiddlewareHandler",
    "WebSocketMiddlewareType",
    "HTTPMiddlewareInterface",
    "WebSocketMiddlewareInterface",
    "DEFAULT_HTTP_MIDDLEWARES",
    "DEFAULT_WEBSOCKET_MIDDLEWARES",
]
