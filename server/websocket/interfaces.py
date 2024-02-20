from abc import abstractmethod
from typing import Callable, overload

from pydantic import BaseModel

from server.utils.supports import Collection

WebSocketMessagePayload = (
    str | dict[str, object] | list[dict[str, object]] | BaseModel | Collection | None
)


class WebSocketInterface:
    """WebSocketInterface is the interface for the WebSocket component."""

    @abstractmethod
    async def start(self) -> None:
        """Start the WebSocket server."""

    @overload
    @abstractmethod
    def add_handler(
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
        """Add a handler for a command."""
