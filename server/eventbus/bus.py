import asyncio
import logging
from collections import defaultdict
from typing import Awaitable, Callable, cast

from server.utils.helpers.function import safe_invokes

from .interfaces import EventBusInterface, Listener, TEvent
from .model import Event

_LOGGER = logging.getLogger(__name__)


class EventBus(EventBusInterface):
    """
    Class for managing events.

    This class provides a central interface for dispatching events and
    managing event listeners.

    Attributes
    ----------
    _listeners : dict[type[Event], list[Listener]
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

    _listeners: dict[type[Event], list[Listener]]

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._listeners = defaultdict(list)

    def add_listener(
        self, event: type[TEvent], listener: Callable[[TEvent], None | Awaitable[None]]
    ) -> None:
        """
        Register a listener for an event.

        Parameters
        ----------
        event : type[Event]
            The event to listen for.
        listener : Callable[[Event], None | Awaitable[None]]
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
        self._listeners.setdefault(event, []).append(cast(Listener, listener))

    def remove_listener(
        self, event: type[TEvent], listener: Callable[[TEvent], None | Awaitable[None]]
    ) -> None:
        """
        Unregister a listener for an event.

        Parameters
        ----------
        event : type[Event]
            The event to stop listening for.

        listener : Callable[[Event], None | Awaitable[None]]
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
        if event in self._listeners:
            try:
                self._listeners[event].remove(cast(Listener, listener))
            except ValueError:
                _LOGGER.warning(
                    "Tried to remove listener for event %s, but it was not registered.",
                    event,
                )

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
        asyncio.create_task(self._async_dispatch(event))

    async def _async_dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered listeners in an async context.

        Parameters
        ----------
        event : Event
            The event to dispatch.
        """
        if event.__class__ in self._listeners:
            await safe_invokes(self._listeners[event.__class__], event)
