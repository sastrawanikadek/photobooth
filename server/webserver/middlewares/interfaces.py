from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from aiohttp import web

from ..models import WebSocketIncomingMessage, WebSocketResponseMessage

HTTPMiddlewareHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]
WebSocketMiddlewareHandler = Callable[
    [web.WebSocketResponse, WebSocketIncomingMessage],
    Awaitable[WebSocketResponseMessage],
]
WebSocketMiddlewareType = Callable[
    [web.WebSocketResponse, WebSocketIncomingMessage, WebSocketMiddlewareHandler],
    Awaitable[WebSocketResponseMessage],
]


class HTTPMiddlewareInterface(ABC):
    """Base class for HTTP middlewares."""

    @abstractmethod
    async def handle(
        self, request: web.Request, handler: HTTPMiddlewareHandler
    ) -> web.StreamResponse:
        """Handle the request."""


class WebSocketMiddlewareInterface(ABC):
    """Base class for WebSocket middlewares."""

    @abstractmethod
    async def handle(
        self,
        connection: web.WebSocketResponse,
        message: WebSocketIncomingMessage,
        handler: WebSocketMiddlewareHandler,
    ) -> WebSocketResponseMessage:
        """Handle the request."""
