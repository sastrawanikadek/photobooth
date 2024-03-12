from server.eventbus import Event

from .interfaces import CameraDeviceInterface


class CameraConnectedEvent(Event):
    """Event that is fired when the camera is connected."""

    _data: CameraDeviceInterface

    def __init__(self, data: CameraDeviceInterface) -> None:
        super().__init__(data)
        self._data = data

    @property
    def data(self) -> CameraDeviceInterface:
        """The data of the event."""
        return self._data


class CameraDisconnectedEvent(Event):
    """Event that is fired when the camera is disconnected."""


class CameraActiveEvent(Event):
    """Event that is fired when the camera is active from being idle."""
