from abc import ABC, abstractmethod

from server.eventbus import EventBusInterface
from server.injector import DependencyContainerInterface, DependencyInjectorInterface
from server.managers.component import ComponentManagerInterface
from server.managers.settings import SettingsManagerInterface
from server.webserver import WebServerInterface


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
    """

    component_manager: ComponentManagerInterface
    dependency_container: DependencyContainerInterface
    dependency_injector: DependencyInjectorInterface
    eventbus: EventBusInterface
    settings_manager: SettingsManagerInterface
    webserver: WebServerInterface

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
