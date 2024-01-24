from abc import ABC, abstractmethod
from typing import Type

from server.eventbus import Event, EventBusInterface, Listener
from server.injector import DependencyContainerInterface, DependencyInjectorInterface
from server.managers.component import ComponentManagerInterface


class PhotoboothInterface(ABC):
    """
    Interface for the core class photobooth.

    Attributes
    ----------
    component_manager : ComponentManagerInterface
        The component manager.
    dependency_container : DependencyContainerInterface
        The dependency container.
    dependency_injector : DependencyInjectorInterface
        The dependency injector.
    eventbus : EventBusInterface
        The eventbus.
    settings_manager : SettingsManagerInterface
        The settings manager.
    """

    component_manager: ComponentManagerInterface
    dependency_container: DependencyContainerInterface
    dependency_injector: DependencyInjectorInterface
    eventbus: EventBusInterface

    @abstractmethod
    def initialize(self) -> None:
        """
        Bootstrap the photobooth.

        Initialize the main components of the photobooth.
        """

    @abstractmethod
    def prepare(self) -> None:
        """
        Prepare the photobooth.

        Load all the necessary components and settings.
        """

    @abstractmethod
    async def startup(self) -> None:
        """Start the photobooth."""


class ServiceProviderInterface:
    """Interface for service providers."""

    dependencies: dict[type, type] = {}
    dependency_container: DependencyContainerInterface
    eventbus: EventBusInterface
    singletons: dict[type, type] = {}
    event_listeners: dict[Type[Event], list[Listener]] = {}

    def __init__(
        self,
        dependency_container: DependencyContainerInterface,
        eventbus: EventBusInterface,
    ) -> None:
        """
        Initialize the service provider.

        Parameters
        ----------
        dependency_container : DependencyContainerInterface
            The dependency container.
        eventbus : EventBusInterface
            The eventbus.
        """
        self.dependency_container = dependency_container
        self.eventbus = eventbus

    def register(self) -> None:
        """
        Register the service provider.

        This method is called on the preparation lifecycle stage.
        """

    def boot(self) -> None:
        """
        Boot the service provider.

        This method is called on the startup lifecycle stage and
        most of the dependencies should be available to be injected.
        """
