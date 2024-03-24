import asyncio
import inspect
import logging
from functools import partial, update_wrapper
from typing import cast

from aiohttp import web

from server.injector import DependencyInjectorInterface
from server.utils.helpers.inspect import class_has_method
from server.utils.helpers.module import get_calling_module

from .interfaces import (
    WebSocketComponentInterface,
    WebSocketHandlerType,
)
from .middlewares import WebSocketMiddlewareHandler, WebSocketMiddlewareType
from .models import (
    WebSocketBroadcastMessage,
    WebSocketErrorEnvelope,
    WebSocketIncomingMessage,
    WebSocketMessageData,
    WebSocketResponseMessage,
)
from .utils import bind_request_model, is_websocket_handler

_LOGGER = logging.getLogger(__name__)


class WebSocketComponent(WebSocketComponentInterface):
    """
    WebSocket component for the web server.

    Attributes
    ----------
    _handlers : dict[str, tuple[type, str] | WebSocketHandlerType]
        A dictionary of message handlers.
    _subscribed_clients : dict[str, list[web.WebSocketResponse]]
        A dictionary of subscribed clients keyed by the channel name.
    """

    _handlers: dict[str, tuple[type, str] | WebSocketHandlerType] = {}
    _subscribed_clients: dict[str, list[web.WebSocketResponse]] = {}
    _middlewares: list[WebSocketMiddlewareType] = []

    def __init__(
        self,
        app: web.Application,
        *,
        injector: DependencyInjectorInterface,
        middlewares: list[WebSocketMiddlewareType] = [],
    ) -> None:
        """
        Initialize the component.

        Parameters
        ----------
        app : web.Application
            The web application.
        injector : DependencyInjectorInterface
            The dependency injector.
        middlewares : list[WebSocketMiddlewareType]
            The middlewares to use.
        """
        self._app = app
        self._injector = injector
        self._middlewares = middlewares

        self._app.add_routes([web.get("/", self._websocket_handler)])

    def add_handler(self, *args: object, **kwargs: object) -> None:
        """
        Add a handler for a command.

        Parameters
        ----------
        *args : object
            The arguments.
        **kwargs : object
            The keyword arguments.

        Raises
        ------
        TypeError
            If the arguments are invalid.
        ValueError
            If a handler for the command is already registered.
            If the method is not found on the class.
        """
        if len(args) == 2 and isinstance(args[0], str) and callable(args[1]):
            return self._add_handler(args[0], args[1])

        if (
            "command" in kwargs
            and "handler" in kwargs
            and isinstance(kwargs["command"], str)
            and callable(kwargs["handler"])
        ):
            return self._add_handler(kwargs["command"], kwargs["handler"])

        if (
            len(args) == 3
            and isinstance(args[0], str)
            and inspect.isclass(args[1])
            and isinstance(args[2], str)
        ):
            return self._add_class_handler(args[0], args[1], args[2])

        if (
            "command" in kwargs
            and "cls" in kwargs
            and "method" in kwargs
            and isinstance(kwargs["command"], str)
            and inspect.isclass(kwargs["cls"])
            and isinstance(kwargs["method"], str)
        ):
            return self._add_class_handler(
                kwargs["command"], kwargs["cls"], kwargs["method"]
            )

        raise TypeError("Invalid arguments")

    def add_middleware(self, middleware: WebSocketMiddlewareType) -> None:
        """
        Add a middleware.

        Parameters
        ----------
        middleware : WebSocketMiddlewareType
            The middleware to add.
        """
        self._middlewares.append(middleware)

    def add_channel(self, channel: str) -> None:
        """
        Add a channel to broadcast to clients via WebSocket.

        Parameters
        ----------
        channel : str
            The channel to add.

        Raises
        ------
        ValueError
            If the channel already exists.
        """
        if channel in self._subscribed_clients:
            raise ValueError(f"Channel {channel} already exists")

        self._subscribed_clients[channel] = []

    def add_channels(self, channels: list[str]) -> None:
        """
        Add a list of channels to broadcast to clients via WebSocket.

        Parameters
        ----------
        channels : list[str]
            The channels to add.
        """
        for channel in channels:
            self.add_channel(channel)

    def remove_channel(self, channel: str) -> None:
        """
        Remove a channel.

        Parameters
        ----------
        channel : str
            The channel to remove.
        """
        if channel in self._subscribed_clients:
            del self._subscribed_clients[channel]

    def subscribe(self, channel: str, websocket: web.WebSocketResponse) -> None:
        """
        Subscribe to a channel.

        Parameters
        ----------
        channel : str
            The channel to subscribe to.
        websocket : web.WebSocketResponse
            The WebSocket connection.

        Raises
        ------
        ValueError
            If the channel does not exist.
        """
        if channel not in self._subscribed_clients:
            raise ValueError(f"Channel {channel} does not exist")

        self._subscribed_clients[channel].append(websocket)

    def unsubscribe(self, channel: str, websocket: web.WebSocketResponse) -> None:
        """
        Unsubscribe from a channel.

        Parameters
        ----------
        channel : str
            The channel to unsubscribe from.
        websocket : web.WebSocketResponse
            The WebSocket connection.

        Raises
        ------
        ValueError
            If the client is not subscribed to the channel.
        """
        if (
            channel in self._subscribed_clients
            and websocket in self._subscribed_clients[channel]
        ):
            self._subscribed_clients[channel].remove(websocket)

    def broadcast(self, channel: str, payload: WebSocketMessageData) -> None:
        """
        Broadcast a message to a channel to all subscribed clients via WebSocket.

        Parameters
        ----------
        channel : str
            The channel to broadcast to.
        payload : WebSocketMessageData
            The payload to broadcast.

        Raises
        ------
        ValueError
            If the channel does not exist.
        """
        if channel not in self._subscribed_clients:
            raise ValueError(f"Channel {channel} does not exist")

        asyncio.create_task(self._async_broadcast(channel, payload))

    def get_subscribers(self, channel: str) -> list[web.WebSocketResponse]:
        """
        Get the subscribers for a channel.

        Parameters
        ----------
        channel : str
            The channel to get the subscribers for.

        Returns
        -------
        list[web.WebSocketResponse]
            The subscribers for the channel.
        """
        return self._subscribed_clients.get(channel, [])

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
            True if the channel has subscribers, otherwise False.
        """
        return bool(self.get_subscribers(channel))

    async def _async_broadcast(
        self, channel: str, payload: WebSocketMessageData
    ) -> None:
        """Broadcast a message to a channel to all subscribed clients via WebSocket asynchronously."""
        messages = [
            websocket.send_str(
                WebSocketBroadcastMessage(
                    channel=channel,
                    payload=payload,
                ).to_json()
            )
            for websocket in self._subscribed_clients[channel]
        ]
        await asyncio.gather(*messages)

    def _add_handler(self, command: str, handler: WebSocketHandlerType) -> None:
        """
        Add a handler for a command.

        Parameters
        ----------
        command : str
            The command to handle.
        handler : callable
            The handler to register.

        Raises
        ------
        ValueError
            If a handler for the command is already registered.
            If the handler is not a valid WebSocket handler.
        """
        if command in self._handlers:
            calling_module = get_calling_module()

            _LOGGER.error(
                "Unable to register handler for command %s from module %s",
                command,
                calling_module.__name__ if calling_module is not None else "unknown",
            )
            raise ValueError(f"Handler for command {command} already registered")

        if not is_websocket_handler(handler):
            raise ValueError("Handler is not a valid WebSocket handler")

        self._handlers[command] = handler

    def _add_class_handler(self, command: str, cls: type, method: str) -> None:
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

        Raises
        ------
        ValueError
            If a handler for the command is already registered.
            If the method is not found on the class.
            If the method is not a valid WebSocket handler.
        """
        if command in self._handlers:
            calling_module = get_calling_module()

            _LOGGER.error(
                "Unable to register handler for command %s from module %s",
                command,
                calling_module.__name__ if calling_module is not None else "unknown",
            )
            raise ValueError(f"Handler for command {command} already registered")

        if not class_has_method(cls, method):
            raise ValueError(f'Method "{method}" not found on class "{cls.__name__}"')

        if not is_websocket_handler(getattr(cls, method)):
            raise ValueError("Method is not a valid WebSocket handler")

        self._handlers[command] = (cls, method)

    async def _websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        Handle WebSocket connections.

        Parameters
        ----------
        request : web.Request
            The request.

        Returns
        -------
        web.WebSocketResponse
            The WebSocket connection.
        """
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)

        async for message in websocket:
            if message.type == web.WSMsgType.TEXT:
                _LOGGER.debug("Received message: %s", message.data)

                try:
                    incoming_message = WebSocketIncomingMessage(**message.json())
                except ValueError:
                    await websocket.send_str(
                        WebSocketResponseMessage(
                            status="error",
                            command="unknown",
                            error=WebSocketErrorEnvelope(
                                message="Invalid message format."
                            ),
                        ).to_json()
                    )
                    continue

                if incoming_message.command not in self._handlers:
                    await websocket.send_str(
                        WebSocketResponseMessage(
                            status="error",
                            command=incoming_message.command,
                            error=WebSocketErrorEnvelope(message="Unknown command."),
                        ).to_json()
                    )
                    return

                handler = self._prepare_middlewares()
                response = await handler(websocket, incoming_message)
                await websocket.send_str(response.to_json())
            elif message.type == web.WSMsgType.ERROR:
                _LOGGER.error(
                    "WebSocket connection closed with exception: %s",
                    websocket.exception(),
                )

        # Remove client from subscribed channels
        for channel in self._subscribed_clients:
            if websocket in self._subscribed_clients[channel]:
                self._subscribed_clients[channel].remove(websocket)

        return websocket

    def _prepare_middlewares(self) -> WebSocketMiddlewareHandler:
        """
        Create a stack of middlewares with the handler at the end.

        Returns
        -------
        WebSocketMiddlewareHandler
            The middleware handler.
        """
        if not self._middlewares:
            return self._run_command_handler

        middlewares = list(reversed(self._middlewares))

        wrapped_handler = update_wrapper(
            partial(middlewares[0], handler=self._run_command_handler),
            self._run_command_handler,
        )

        for middleware in middlewares[1:]:
            wrapped_handler = update_wrapper(
                partial(middleware, handler=wrapped_handler),
                wrapped_handler,
            )

        return wrapped_handler

    async def _run_command_handler(
        self,
        websocket: web.WebSocketResponse,
        incoming_message: WebSocketIncomingMessage,
    ) -> WebSocketResponseMessage:
        """
        Run the handler for a command.

        Parameters
        ----------
        websocket : web.WebSocketResponse
            The WebSocket connection.
        incoming_message : WebSocketIncomingMessage
            The incoming message.

        Returns
        -------
        WebSocketResponseMessage
            The response message.
        """
        with self._injector.add_temporary_container() as container:
            container.singleton(web.WebSocketResponse, websocket)

            handler = self._get_command_handler(incoming_message.command)

            bind_request_model(container, handler, incoming_message.payload)

            response = await self._injector.call_with_injection(handler)
            response.command = incoming_message.command

        return response

    def _get_command_handler(self, command: str) -> WebSocketHandlerType:
        """
        Get the handler for a command.

        Parameters
        ----------
        command : str
            The command to get the handler for.

        Returns
        -------
        WebSocketHandlerType
            The handler for the command.
        """
        handler_value = self._handlers[command]

        if callable(handler_value):
            return handler_value

        cls, method = handler_value
        instance: object = self._injector.inject_constructor(cls)
        return cast(WebSocketHandlerType, getattr(instance, method))
