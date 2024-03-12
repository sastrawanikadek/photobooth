import logging

from aiohttp import web

from server.injector import DependencyInjectorInterface

from .constants import HOST, PORT
from .exception_handlers import HTTPExceptionHandler, WebSocketExceptionHandler
from .http import HTTPComponent
from .interfaces import WebServerInterface
from .websocket import WebSocketComponent

_LOGGER = logging.getLogger(__name__)


class WebServer(WebServerInterface):
    """A web server that provides HTTP and WebSocket communication."""

    def __init__(self, injector: DependencyInjectorInterface) -> None:
        self._app = web.Application()
        self._http_exception_handler = HTTPExceptionHandler()
        self._websocket_exception_handler = WebSocketExceptionHandler()

        self.http = HTTPComponent(self._app, injector, self._http_exception_handler)
        self.websocket = WebSocketComponent(
            self._app, injector, self._websocket_exception_handler
        )

    async def start(self) -> None:
        """Start the web server."""
        runner = web.AppRunner(self._app)
        await runner.setup()

        site = web.TCPSite(runner, HOST, PORT)
        await site.start()

        # Register the exception handlers
        self._http_exception_handler.register()
        self._websocket_exception_handler.register()

        _LOGGER.info(f"Web server started on {site.name}")
