from abc import abstractmethod
from typing import Callable, Optional

from managers.component import ComponentInterface

WebSocketMessagePayload = Optional[dict[str, object] | list[dict[str, object]]]


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
