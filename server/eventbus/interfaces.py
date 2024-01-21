from abc import ABC, abstractmethod
from typing import Awaitable, Callable, TypeVar

from .model import Event

TEvent = TypeVar("TEvent", bound=Event)
Listener = Callable[[Event], None | Awaitable[None]]


class EventBusInterface(ABC):
    """Interface for event bus implementations."""

    @abstractmethod
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
        """

    @abstractmethod
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
        """

    @abstractmethod
    def dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered listeners.

        Parameters
        ----------
        event : Event
            The event to dispatch.
        """
