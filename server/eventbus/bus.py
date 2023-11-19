from collections import defaultdict
from typing import Type

from .interface import EventBusInterface, Listener
from .model import Event


class EventBus(EventBusInterface):
    """
    Class for managing events.

    This class provides a central interface for dispatching events and
    managing event listeners.

    Attributes
    ----------
    listeners : dict[str, list[Callable[[Event], None]]]
        A dictionary of event listeners, keyed by event identifier.

    Examples
    --------
    >>> from eventbus import EventBus, Event
    >>> bus = EventBus()
    >>> def listener(event):
    ...     print(event)
    ...
    >>> bus.add_listener(Event, listener)
    >>> bus.dispatch(Event("test"))
    Event(event_type='test', event_data=None, timestamp=datetime.datetime(2021, 5, 31, 21, 4, 21, 114361))
    """

    def __init__(self) -> None:
        """Initialize the event bus."""
        self.listeners = defaultdict(list)

    def add_listener(self, event: Type[Event], listener: Listener) -> None:
        """
        Register a listener for an event.

        Parameters
        ----------
        event : type[Event]
            The event to listen for.
        listener : Callable[[Event], None]
            The listener to register.

        Examples
        --------
        >>> from eventbus import EventBus, Event
        >>> bus = EventBus()
        >>> def listener(event):
        ...     print(event)
        ...
        >>> bus.add_listener(Event, listener)
        """
        if event not in self.listeners:
            self.listeners[event] = []

        self.listeners[event].append(listener)

    def remove_listener(self, event: Type[Event], listener: Listener) -> None:
        """
        Unregister a listener for an event.

        Parameters
        ----------
        event : type[Event]
            The event to stop listening for.

        listener : Callable[[Event], None]
            The listener to unregister.

        Raises
        ------
        ValueError
            If the listener is not registered for the event.

        Examples
        --------
        >>> from eventbus import EventBus, Event
        >>> bus = EventBus()
        >>> def listener(event):
        ...     print(event)
        ...
        >>> bus.add_listener(Event, listener)
        >>> bus.remove_listener(Event, listener)
        """
        if event in self.listeners:
            try:
                self.listeners[event].remove(listener)
            except ValueError:
                # TODO: Log this
                pass

    def dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered listeners.

        Parameters
        ----------
        event : Event
            The event to dispatch.

        Examples
        --------
        >>> from eventbus import EventBus, Event
        >>> bus = EventBus()
        >>> def listener(event):
        ...     print(event)
        ...
        >>> bus.add_listener(Event, listener)
        >>> bus.dispatch(Event("test"))
        Event(event_type='test', event_data=None, timestamp=datetime.datetime(2021, 5, 31, 21, 4, 21, 114361))
        """
        if event.__class__ in self.listeners:
            for listener in self.listeners[event.__class__]:
                listener(event)
