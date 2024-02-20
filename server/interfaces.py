from abc import ABC, abstractmethod
from typing import Awaitable, Callable, TypeVar

from server.eventbus import Event, EventBusInterface
from server.injector import DependencyContainerInterface, DependencyInjectorInterface
from server.managers.component import ComponentInterface, ComponentManagerInterface
from server.managers.settings import SettingSchema, SettingsManagerInterface
from server.utils.pydantic_fields import SlugStr
from server.websocket import WebSocketInterface

TEvent = TypeVar("TEvent", bound=Event)
TClass = TypeVar("TClass", bound=object)
TReturn = TypeVar("TReturn", bound=object)
TDefault = TypeVar("TDefault", bound=object)


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
    websocket : WebSocketInterface
        The websocket server.
    """

    component_manager: ComponentManagerInterface
    dependency_container: DependencyContainerInterface
    dependency_injector: DependencyInjectorInterface
    eventbus: EventBusInterface
    settings_manager: SettingsManagerInterface
    websocket: WebSocketInterface

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


class PhotoboothAppInterface(ABC):
    """Interface for the photobooth app."""

    @abstractmethod
    def dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered listeners.

        Parameters
        ----------
        event : Event
            The event to dispatch.
        """

    @abstractmethod
    def listen(
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
    def bind(
        self, interface: type, implementation: type | Callable[..., object]
    ) -> None:
        """
        Bind an interface to an implementation.

        Implementations are instantiated every time they are injected.

        Parameters
        ----------
        interface : type
            The interface to bind.
        implementation : type | Callable[..., object]
            The implementation or factory to bind to the interface.
        """

    @abstractmethod
    def singleton(
        self, interface: type, implementation: object | Callable[[], object]
    ) -> None:
        """
        Bind an interface to a singleton implementation.

        Implementations are only instantiated once and then reused.

        Parameters
        ----------
        interface : type
            The interface to bind.
        implementation : object | Callable[[], object]
            The instance or factory to bind to the interface.
        """

    @abstractmethod
    def resolve(self, interface: type) -> object:
        """
        Resolve an implementation for an interface.

        Parameters
        ----------
        interface : type
            The interface to resolve.

        Returns
        -------
        object
            The implementation for the interface.
        """

    @abstractmethod
    def inject_constructor(self, cls: type[TClass]) -> TClass:
        """
        Inject dependencies into a class.

        Parameters
        ----------
        cls : type
            The class to inject dependencies into.

        Returns
        -------
        object
            The class with injected dependencies.
        """

    @abstractmethod
    async def call_with_injection(self, func: Callable[..., TReturn]) -> TReturn:
        """
        Call a function with dependency injection.

        Parameters
        ----------
        func : callable
            The function to call.

        Returns
        -------
        object
            The result of the function.
        """

    @abstractmethod
    def get_component(self, slug: str) -> ComponentInterface | None:
        """
        Get a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to get.

        Returns
        -------
        ComponentInterface | None
            The component with the given slug or None if not installed.
        """

    @abstractmethod
    def get_component_data(self, slug: str) -> dict[str, object] | None:
        """
        Get the data of a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component data to get.

        Returns
        -------
        dict[str, object] | None
            The data of the component with the given slug or None if component is not installed.
        """

    @abstractmethod
    async def add_setting_schema(
        self, source: str, schema: SettingSchema, persist: bool = False
    ) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        persist : bool
            Whether to persist the schema to the database, by default False.
        """

    @abstractmethod
    async def add_setting_schemas(
        self,
        schemas: dict[SlugStr, list[SettingSchema]],
        *,
        persist: bool = False,
        schema_only: bool = False,
    ) -> None:
        """
        Add a new settings schema to the settings manager.

        Parameters
        ----------
        schemas : dict[SlugStr, list[SettingSchema]]
            The schemas of the settings to add, keyed by their source.
        persist : bool
            Whether to persist the schema to the database, by default False.
        schema_only : bool
            Whether to only add the schema to the settings manager, by default False.
        """

    @abstractmethod
    def get_setting_value(
        self, source: str, key: str, default: TDefault | None = None
    ) -> object | TDefault | None:
        """
        Get a setting value by its source and key.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        key : str
            The key of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given source and key or the default value if it does not exist.
        """

    @abstractmethod
    def set_setting_value(self, source: str, key: str, value: object) -> None:
        """
        Set a setting value by its source and key.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        key : str
            The key of the setting.
        value : object
            The value of the setting.
        """
