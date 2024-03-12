from server.eventbus import Event, EventBusInterface, Listener
from server.injector import DependencyContainerInterface
from server.managers.settings import SettingSchema
from server.webserver import Route


class ServiceProvider:
    """Base class for service providers."""

    channels: list[str] = []
    """
    List of the channels that will be registered to the websocket server which
    can be used to send messages to the clients.
    """

    dependencies: dict[type, type] = {}
    """
    The dependencies that the service provider provides, where the key is the
    dependency interface and the value is the dependency implementation.
    
    New instances of the dependencies will be created for each request.
    """

    dependency_container: DependencyContainerInterface
    eventbus: EventBusInterface

    singletons: dict[type, type] = {}
    """
    The singletons that the service provider provides, where the key is the
    singleton interface and the value is the singleton implementation.
    
    Singletons are type of dependencies that are created only once and then
    reused for each request.
    """

    setting_schemas: dict[str, list[SettingSchema]] = {}
    """
    The setting schemas that the service provider provides, where the key is
    the setting source and the value is the list of setting schemas.
    """

    event_listeners: dict[type[Event], list[Listener]] = {}
    """
    Registered listeners for the events. The key is the event class and the
    value is the list of listeners which is a function that takes the event
    as the first argument.
    """

    routes: list[Route] = []
    """
    List of the API routes that the module provides. The routes are used to
    register the API handlers to the webserver.
    """

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
