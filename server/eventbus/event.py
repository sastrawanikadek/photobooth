import logging
from typing import cast

import pendulum

from server.utils.helpers.serialization import json_serialize
from server.webserver import WebSocketMessageData

_LOGGER = logging.getLogger(__name__)


class Event:
    """Base class for events."""

    def __init__(self, data: object | None = None) -> None:
        """
        Initialize the event.

        Parameters
        ----------
        data : object | None
            The data associated with the event.
        """
        self._data = data
        self._timestamp = pendulum.now()

    @property
    def name(self) -> str:
        """The name of the event."""
        return self.__class__.__name__

    @property
    def data(self) -> object:
        """The data of the event."""
        return self._data

    @property
    def timestamp(self) -> pendulum.DateTime:
        """The timestamp of the event."""
        return self._timestamp

    def broadcast(self, channel: str) -> None:
        """Broadcast the event to channel subscribers via the WebSocket."""
        from server.proxy import app

        _LOGGER.debug(f"Broadcasting event: {self}")

        try:
            broadcast_data = (
                cast(WebSocketMessageData, self._data)
                if json_serialize(self._data)
                else None
            )
            app().broadcast(channel, broadcast_data)
        except TypeError:
            app().broadcast(channel, None)

    def dispatch(self) -> None:
        """Dispatch the event to all registered listeners."""
        from server.proxy import app

        _LOGGER.debug(f"Dispatching event: {self}")
        app().dispatch(self)

    def __repr__(self) -> str:
        return f"<{self.name} data={self.data} timestamp={self.timestamp}>"
