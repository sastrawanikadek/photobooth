import json
import logging
from typing import Callable

from pydantic import BaseModel
from websockets import WebSocketServerProtocol, serve

from server.eventbus import EventBusInterface
from server.events import AppReadyEvent
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
    _eventbus : EventBusInterface
        The event bus.
    _injector : DependencyInjectorInterface
        The dependency injector.
    _handlers : dict[str, Callable[..., None]]
        A dictionary of command handlers, keyed by command.
    """

    _eventbus: EventBusInterface
    _injector: DependencyInjectorInterface
    _handlers: dict[str, Callable[..., WebSocketMessagePayload]]

    def __init__(
        self, eventbus: EventBusInterface, injector: DependencyInjectorInterface
    ) -> None:
        """Initialize the component."""

        self._eventbus = eventbus
        self._injector = injector
        self._handlers = {}

        self._eventbus.add_listener(AppReadyEvent, self._on_app_ready)

    async def _on_app_ready(self, _: AppReadyEvent) -> None:
        """
        Handler for the AppReadyEvent.

        This handler starts the WebSocket server.
        """
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

        handler = self._handlers[incoming_message.command]

        with self._injector.add_temporary_container() as container:
            container.bind(WebSocketServerProtocol, websocket)

            model = get_first_match_signature(handler, BaseModel)
            if model is not None and incoming_message.payload is not None:
                try:
                    container.bind(model, model(**incoming_message.payload))
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

    def add_handler(self, command: str, handler: Callable[..., None]) -> None:
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
