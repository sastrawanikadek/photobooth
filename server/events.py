from dataclasses import dataclass, field

from server.eventbus import Event


@dataclass(frozen=True)
class AppInitializedEvent(Event):
    """Event that is fired when the app is initialized."""

    event_type: str = field(default="app_initialized", init=False)


@dataclass(frozen=True)
class AppStartupEvent(Event):
    """Event that is fired when the app is starting up."""

    event_type: str = field(default="app_startup", init=False)


@dataclass(frozen=True)
class AppReadyEvent(Event):
    """Event that is fired when the app is ready to serve requests."""

    event_type: str = field(default="app_ready", init=False)
