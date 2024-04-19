from abc import ABC, abstractmethod

from server.dependency_injection.interfaces import (
    DependencyContainerInterface,
    DependencyInjectorInterface,
)
from server.eventbus.interfaces import EventBusInterface
from server.managers.components.interfaces import ComponentManagerInterface
from server.managers.settings.interfaces import SettingsManagerInterface
from server.managers.storages.interfaces import StorageManagerInterface
from server.webserver.interfaces import WebServerInterface


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
    webserver : WebServerInterface
        The webserver.
    storage_manager : StorageManagerInterface
        The storage manager.
    """

    component_manager: ComponentManagerInterface
    dependency_container: DependencyContainerInterface
    dependency_injector: DependencyInjectorInterface
    eventbus: EventBusInterface
    settings_manager: SettingsManagerInterface
    webserver: WebServerInterface
    storage_manager: StorageManagerInterface

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
