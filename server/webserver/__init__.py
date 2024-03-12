"""Module for the WebServer to provide HTTP and WebSocket communication."""

from .api_handlers.websocket import WebSocketAPIHandler
from .interfaces import (
    HTTPHandlerType,
    RouteMethod,
    WebServerInterface,
    WebSocketHandlerType,
    WebSocketMessageData,
)
from .models import (
    WebSocketErrorEnvelope,
    WebSocketIncomingMessage,
    WebSocketResponseMessage,
)
from .route import Route
from .server import WebServer

__all__ = [
    "HTTPHandlerType",
    "Route",
    "RouteMethod",
    "WebSocketHandlerType",
    "WebServer",
    "WebSocketAPIHandler",
    "WebServerInterface",
    "WebSocketMessageData",
    "WebSocketIncomingMessage",
    "WebSocketResponseMessage",
    "WebSocketErrorEnvelope",
]
