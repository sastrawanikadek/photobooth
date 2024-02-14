import json
import logging
from typing import Callable

from pydantic import BaseModel
from websockets import WebSocketServerProtocol, serve

from server.injector import DependencyInjectorInterface
from server.utils.helpers.inspect import get_first_match_signature
from server.utils.helpers.module import get_calling_module

from .constants import HOST, PORT
from .exceptions import WebSocketHandlerError
from .interfaces import WebSocketInterface, WebSocketMessagePayload
from .models import (
    WebSocketErrorResponse,
    WebSocketIncomingMessage,
    WebSocketSuccessResponse,
)

_LOGGER = logging.getLogger(__name__)


class WebSocket(WebSocketInterface):
    """
    WebSocket is the component for managing WebSocket connections and handling WebSocket messages.

    Attributes
    ----------
    _injector : DependencyInjectorInterface
        The dependency injector.
    _handlers : dict[str, Callable[..., None]]
        A dictionary of command handlers, keyed by command.
    """

    _injector: DependencyInjectorInterface
    _handlers: dict[str, tuple[type, str] | Callable[..., WebSocketMessagePayload]]

    def __init__(self, injector: DependencyInjectorInterface) -> None:
        """Initialize the component."""

        self._injector = injector
        self._handlers = {}

    async def start(self) -> None:
        """Start the WebSocket server."""
        server = await serve(self._on_message, HOST, PORT)
        _LOGGER.info("WebSocket server started on %s:%s", HOST, PORT)

        await server.serve_forever()

    async def _on_message(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handler for WebSocket messages.

        Parameters
        ----------
        websocket : WebSocketServerProtocol
            The WebSocket connection.
        """
        async for message in websocket:
            _LOGGER.debug("Received message: %s", message)

            try:
                incoming_message = WebSocketIncomingMessage(**json.loads(message))
            except ValueError:
                await websocket.send(
                    WebSocketErrorResponse(
                        command="unknown",
                        message="Invalid message format.",
                    ).to_json()
                )
                continue

            await self._run_handler(websocket, incoming_message)

    async def _run_handler(
        self,
        websocket: WebSocketServerProtocol,
        incoming_message: WebSocketIncomingMessage,
    ) -> None:
        """
        Run the handler for a command.

        Parameters
        ----------
        websocket : WebSocketServerProtocol
            The WebSocket connection.
        incoming_message : WebSocketIncomingMessage
            The incoming message.
        """
        if incoming_message.command not in self._handlers:
            await websocket.send(
                WebSocketErrorResponse(
                    command=incoming_message.command,
                    message="Unknown command.",
                ).to_json()
            )
            return

        handler_value = self._handlers[incoming_message.command]

        if callable(handler_value):
            handler = handler_value
        else:
            cls, method = handler_value
            instance: object = self._injector.inject_constructor(cls)
            handler = getattr(instance, method)

        with self._injector.add_temporary_container() as container:
            container.singleton(WebSocketServerProtocol, websocket)

            model = get_first_match_signature(handler, BaseModel)
            if model is not None and isinstance(incoming_message.payload, dict):
                try:
                    container.singleton(model, model(**incoming_message.payload))
                except ValueError:
                    await websocket.send(
                        WebSocketErrorResponse(
                            command=incoming_message.command,
                            message="Invalid payload.",
                        ).to_json()
                    )
                    return

            try:
                response = await self._injector.call_with_injection(handler)
            except WebSocketHandlerError as error:
                _LOGGER.warning(
                    f'Error in handler for command "{incoming_message.command}": {error.message}',
                )
                await websocket.send(
                    WebSocketErrorResponse(
                        command=incoming_message.command,
                        message=error.message,
                    ).to_json()
                )
                return

        await websocket.send(
            WebSocketSuccessResponse(
                command=incoming_message.command,
                payload=response,
            ).to_json()
        )

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
            and isinstance(args[1], type)
            and isinstance(args[2], str)
        ):
            return self._add_class_handler(args[0], args[1], args[2])

        if (
            "command" in kwargs
            and "cls" in kwargs
            and "method" in kwargs
            and isinstance(kwargs["command"], str)
            and isinstance(kwargs["cls"], type)
            and isinstance(kwargs["method"], str)
        ):
            return self._add_class_handler(
                kwargs["command"], kwargs["cls"], kwargs["method"]
            )

        raise TypeError("Invalid arguments")

    def _add_handler(
        self, command: str, handler: Callable[..., WebSocketMessagePayload]
    ) -> None:
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
        """
        if command in self._handlers:
            calling_module = get_calling_module()

            _LOGGER.error(
                "Unable to register handler for command %s from module %s",
                command,
                calling_module.__name__ if calling_module is not None else "unknown",
            )
            raise ValueError(f"Handler for command {command} already registered")

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
        """
        if command in self._handlers:
            calling_module = get_calling_module()

            _LOGGER.error(
                "Unable to register handler for command %s from module %s",
                command,
                calling_module.__name__ if calling_module is not None else "unknown",
            )
            raise ValueError(f"Handler for command {command} already registered")

        if not hasattr(cls, method):
            raise ValueError(f'Method "{method}" not found on class "{cls.__name__}"')

        self._handlers[command] = (cls, method)
