from dataclasses import dataclass, field

from server.eventbus import Event


@dataclass(frozen=True)
class CameraConnectedEvent(Event):
    """Event that is fired when the camera is connected."""

    event_type: str = field(default="camera_connected", init=False)


@dataclass(frozen=True)
class CameraDisconnectedEvent(Event):
    """Event that is fired when the camera is disconnected."""

    event_type: str = field(default="camera_disconnected", init=False)


@dataclass(frozen=True)
class CameraActiveEvent(Event):
    """Event that is fired when the camera is active."""

    event_type: str = field(default="camera_active", init=False)
