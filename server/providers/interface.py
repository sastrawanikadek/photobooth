from typing import Callable

from server.eventbus import Event, EventBusInterface, Listener
from server.injector import DependencyContainerInterface
from server.managers.settings import SettingSchema
from server.websocket import WebSocketMessagePayload


class ServiceProviderInterface:
    """Interface for service providers."""

    dependencies: dict[type, type] = {}
    dependency_container: DependencyContainerInterface
    eventbus: EventBusInterface
    singletons: dict[type, type] = {}
    setting_schemas: dict[str, list[SettingSchema]] = {}
    event_listeners: dict[type[Event], list[Listener]] = {}
    websocket_routes: list[
        tuple[str, Callable[..., WebSocketMessagePayload]] | tuple[str, type, str]
    ] = []

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
