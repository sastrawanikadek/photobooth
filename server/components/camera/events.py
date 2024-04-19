from server.eventbus.event import Event, NoDataEvent

from .interfaces import CameraDeviceInterface


class CameraConnectedEvent(Event[CameraDeviceInterface]):
    """Event that is fired when the camera is connected."""


class CameraDisconnectedEvent(NoDataEvent):
    """Event that is fired when the camera is disconnected."""


class CameraActiveEvent(NoDataEvent):
    """Event that is fired when the camera is active from being idle."""
