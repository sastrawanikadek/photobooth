from abc import ABC, abstractmethod
from pathlib import Path
from typing import Awaitable, Callable, Literal, TypeAlias, overload

from aiohttp import web
from pydantic import BaseModel

from server.utils.supports.collection import Collection

from .middlewares import WebSocketMiddlewareType
from .models import WebSocketResponseMessage

RouteMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
WebSocketMessageData: TypeAlias = (
    str | dict[str, object] | list[dict[str, object]] | BaseModel | Collection | None
)

HTTPHandlerType = Callable[..., web.StreamResponse]
WebSocketHandlerType = Callable[..., WebSocketResponseMessage]
ExpectHandlerType = Callable[[web.Request], Awaitable[web.StreamResponse | None]]


class WebServerInterface(ABC):
    """
    Interface for the web server.

    Attributes
    ----------
    http : HTTPComponentInterface
        The HTTP component.
    websocket : WebSocketComponentInterface
        The WebSocket component.
    """

    http: "HTTPComponentInterface"
    websocket: "WebSocketComponentInterface"

    @abstractmethod
    async def start(self) -> None:
        """Start the web server."""

    @property
    @abstractmethod
    def address(self) -> str:
        """Get the address of the web server."""


class HTTPComponentInterface(ABC):
    """Interface for the HTTP component of the web server."""

    @overload
    @abstractmethod
    def add_route(
        self, method: RouteMethod, path: str, handler: HTTPHandlerType, **kwargs: object
    ) -> None:
        """
        Add a route.

        Parameters
        ----------
        method : RouteMethod
            The HTTP method.
        path : str
            The path of the route.
        handler : HTTPHandlerType
            The handler to register.
        **kwargs : object
            Additional keyword arguments.
        """

    @overload
    @abstractmethod
    def add_route(
        self,
        method: RouteMethod,
        path: str,
        cls: type,
        cls_method_name: str,
        **kwargs: object,
    ) -> None:
        """
        Add a route.

        Parameters
        ----------
        method : RouteMethod
            The HTTP method.
        path : str
            The path of the route.
        cls : type
            The class to instantiate.
        cls_method_name : str
            The method to call.
        **kwargs : object
            Additional keyword arguments.
        """

    @abstractmethod
    def add_route(
        self, method: RouteMethod, path: str, *args: object, **kwargs: object
    ) -> None:
        """
        Add a route.

        Parameters
        ----------
        method : RouteMethod
            The HTTP method.
        path : str
            The path of the route.
        *args : object
            The arguments.
        **kwargs : object
            Additional keyword arguments.
        """

    @abstractmethod
    def add_static_route(
        self,
        path: str,
        directory: str | Path,
        *,
        name: str | None = None,
        expect_handler: ExpectHandlerType | None = None,
        chunk_size: int = 256 * 1024,
        show_index: bool = False,
        follow_symlinks: bool = False,
        append_version: bool = False,
    ) -> None:
        """
        Add a route for serving static files.

        Parameters
        ----------
        path : str
            The path of the route.
        directory : str | Path
            The directory to serve files from.
        name : str | None
            The name of the route.
        expect_handler : callable[web.Request, Awaitable[web.StreamResponse | None]] | None
            The expect handler.
        chunk_size : int
            Size of single chunk for file downloading, 256Kb by default.

            Increasing chunk_size parameter to, say,
            1Mb may increase file downloading speed but consumes more memory.
        show_index : bool
            Flag for allowing to show indexes of a directory,
            by default it's not allowed and HTTP/403 will be returned on directory access.
        follow_symlinks : bool
            Flag for allowing to follow symlinks that lead outside the static root directory,
            by default it's not allowed and HTTP/404 will be returned on access
        append_version : bool
            Flag for adding file version (hash) to the url query string to avoid caching issues.
        """

    @abstractmethod
    def get_route(self, name: str) -> web.AbstractResource | None:
        """
        Get a route by its name.

        Parameters
        ----------
        name : str
            The name of the route.

        Returns
        -------
        web.AbstractResource | None
            The route with the given name or None if not found.
        """


class WebSocketComponentInterface(ABC):
    """Interface for the WebSocket component of the web server."""

    @overload
    @abstractmethod
    def add_handler(self, command: str, handler: WebSocketHandlerType) -> None:
        """
        Add a handler for a command.

        Parameters
        ----------
        command : str
            The command to handle.
        handler : callable
            The handler to register.
        """

    @overload
    @abstractmethod
    def add_handler(self, command: str, cls: type, method: str) -> None:
        """
        Add a handler for a command.

        Parameters
        ----------
        command : str
            The command to handle.
        cls : type
            The class to instantiate.
        method : str
            The method to call.
        """

    @abstractmethod
    def add_handler(self, *args: object, **kwargs: object) -> None:
        """
        Add a handler for a command.

        Parameters
        ----------
        *args : object
            The arguments.
        **kwargs : object
            The keyword arguments.
        """

    @abstractmethod
    def add_middleware(self, middleware: WebSocketMiddlewareType) -> None:
        """
        Add a middleware.

        Parameters
        ----------
        middleware : WebSocketMiddlewareType
            The middleware to add.
        """

    @abstractmethod
    def add_channel(self, channel: str) -> None:
        """
        Add a channel to broadcast to clients via WebSocket.

        Parameters
        ----------
        channel : str
            The channel to add.
        """

    @abstractmethod
    def add_channels(self, channels: list[str]) -> None:
        """
        Add a list of channels to broadcast to clients via WebSocket.

        Parameters
        ----------
        channels : list[str]
            The channels to add.
        """

    @abstractmethod
    def remove_channel(self, channel: str) -> None:
        """
        Remove a channel.

        Parameters
        ----------
        channel : str
            The channel to remove.
        """

    @abstractmethod
    def subscribe(self, channel: str, websocket: web.WebSocketResponse) -> None:
        """
        Subscribe to a channel.

        Parameters
        ----------
        channel : str
            The channel to subscribe to.
        websocket : web.WebSocketResponse
            The WebSocket connection.
        """

    @abstractmethod
    def unsubscribe(self, channel: str, websocket: web.WebSocketResponse) -> None:
        """
        Unsubscribe from a channel.

        Parameters
        ----------
        channel : str
            The channel to unsubscribe from.
        websocket : web.WebSocketResponse
            The WebSocket connection.
        """

    @abstractmethod
    def broadcast(self, channel: str, payload: WebSocketMessageData) -> None:
        """
        Broadcast a message to a channel to all subscribed clients via WebSocket.

        Parameters
        ----------
        channel : str
            The channel to broadcast to.
        payload : WebSocketMessageData
            The payload to broadcast.
        """

    @abstractmethod
    def get_subscribers(self, channel: str) -> list[web.WebSocketResponse]:
        """
        Get the subscribers of a channel.

        Parameters
        ----------
        channel : str
            The channel to get the subscribers of.

        Returns
        -------
        list[web.WebSocketResponse]
            The subscribers of the channel.
        """

    @abstractmethod
    def has_subscribers(self, channel: str) -> bool:
        """
        Check if a channel has subscribers.

        Parameters
        ----------
        channel : str
            The channel to check.

        Returns
        -------
        bool
            True if the channel has subscribers, False otherwise.
        """
