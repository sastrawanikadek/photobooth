from abc import abstractmethod
from typing import Callable

from server.managers.component import ComponentInterface

WebSocketMessagePayload = str | dict[str, object] | list[dict[str, object]] | None


class WebSocketInterface(ComponentInterface):
    """WebSocketInterface is the interface for the WebSocket component."""

    @abstractmethod
    def add_handler(self, command: str, handler: Callable[..., None]) -> None:
        """
        Add a handler for a command.

        Parameters
        ----------
        command : str
            The command to handle.
        handler : callable
            The handler to register.
        """
