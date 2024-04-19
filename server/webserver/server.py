import logging

from aiohttp import typedefs, web

from server.constants import PUBLIC_STORAGE_PATH
from server.dependency_injection.interfaces import DependencyInjectorInterface

from .constants import HOST, PORT
from .http import HTTPComponent
from .interfaces import WebServerInterface
from .middlewares import (
    DEFAULT_HTTP_MIDDLEWARES,
    DEFAULT_WEBSOCKET_MIDDLEWARES,
    HTTPMiddlewareInterface,
    WebSocketMiddlewareInterface,
    WebSocketMiddlewareType,
)
from .websocket import WebSocketComponent

_LOGGER = logging.getLogger(__name__)


class WebServer(WebServerInterface):
    """A web server that provides HTTP and WebSocket communication."""

    _site: web.TCPSite | None = None

    def __init__(self, injector: DependencyInjectorInterface) -> None:
        self._injector = injector
        self._app = web.Application(
            middlewares=self._register_http_middlewares(DEFAULT_HTTP_MIDDLEWARES)
        )
        self._runner = web.AppRunner(self._app)

        self.http = HTTPComponent(self._app, injector=injector)
        self.websocket = WebSocketComponent(
            self._app,
            injector=injector,
            middlewares=self._register_websocket_middlewares(
                DEFAULT_WEBSOCKET_MIDDLEWARES
            ),
        )

    async def start(self) -> None:
        """Start the web server."""
        self.http.add_static_route(
            "/static/public", PUBLIC_STORAGE_PATH, name="public", append_version=True
        )

        await self._runner.setup()

        self._site = web.TCPSite(self._runner, HOST, PORT)
        await self._site.start()

        _LOGGER.info(f"Web server started on {self._site.name}")

    @property
    def address(self) -> str:
        """Get the address of the web server."""
        if self._site is None:
            raise RuntimeError("Web server is not running")

        sitename: str = self._site.name
        return sitename

    def _register_http_middlewares(
        self, middlewares: list[type[HTTPMiddlewareInterface] | HTTPMiddlewareInterface]
    ) -> list[typedefs.Middleware]:
        """Register HTTP middlewares."""
        return [
            self._register_http_middleware(middleware) for middleware in middlewares
        ]

    def _register_http_middleware(
        self, middleware: type[HTTPMiddlewareInterface] | HTTPMiddlewareInterface
    ) -> typedefs.Middleware:
        """Register an HTTP middleware."""
        if isinstance(middleware, HTTPMiddlewareInterface):
            instance = middleware
        else:
            instance = self._injector.inject_constructor(middleware)

        return web.middleware(
            lambda request, handler: instance.handle(request, handler)
        )

    def _register_websocket_middlewares(
        self,
        middlewares: list[
            type[WebSocketMiddlewareInterface] | WebSocketMiddlewareInterface
        ],
    ) -> list[WebSocketMiddlewareType]:
        """Register WebSocket middlewares."""
        middleware_handlers: list[WebSocketMiddlewareType] = []

        for middleware in middlewares:
            if isinstance(middleware, WebSocketMiddlewareInterface):
                instance = middleware
            else:
                instance = self._injector.inject_constructor(middleware)

            middleware_handlers.append(instance.handle)

        return middleware_handlers
