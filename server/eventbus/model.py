from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Event:
    """
    Base class for events.

    Attributes
    ----------
    event_type : str
        The type of event.
    event_data : dict | list
        The data associated with the event.
    timestamp : datetime
        The timestamp of the event.

    Examples
    --------
    >>> from eventbus import Event
    >>> event = Event("test", {"message": "test message"})
    >>> event.event_type
    'test'
    >>> event.event_data
    {'message': 'test message'}
    >>> event.timestamp
    datetime.datetime(2021, 5, 31, 21, 4, 21, 114361)
    """

    event_type: str
    event_data: Optional[dict | list] = None
    timestamp: datetime = field(default_factory=datetime.now, init=False)

    def to_dict(self) -> dict:
        """Dictionary representation of the event."""
        return {
            "event_type": self.event_type,
            "event_data": self.event_data,
            "timestamp": self.timestamp.isoformat(),
        }
