from abc import ABC, abstractmethod
from typing import Callable, Literal, TypeAlias, overload

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
