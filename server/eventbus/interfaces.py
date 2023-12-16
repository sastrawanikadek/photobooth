from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Type

from .model import Event

Listener = Callable[[Event], None | Awaitable[None]]


class EventBusInterface(ABC):
    """Interface for event bus implementations."""

    @abstractmethod
    def add_listener(self, event: Type[Event], listener: Listener) -> None:
        """
        Register a listener for an event.

        Parameters
        ----------
        event : type[Event]
            The event to listen for.
        listener : Listener
            The listener to register.
        """

    @abstractmethod
    def remove_listener(self, event: Type[Event], listener: Listener) -> None:
        """
        Unregister a listener for an event.

        Parameters
        ----------
        event : type[Event]
            The event to stop listening for.
        listener : Listener
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
