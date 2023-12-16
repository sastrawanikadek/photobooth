from dataclasses import dataclass, field

from eventbus import Event


@dataclass(frozen=True)
class AppReadyEvent(Event):
    """Event that is fired when the app is ready to serve requests."""

    event_type: str = field(default="app_ready", init=False)
