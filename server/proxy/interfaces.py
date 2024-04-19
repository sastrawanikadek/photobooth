from abc import abstractmethod
from typing import TYPE_CHECKING, Awaitable, Callable, Optional, TypeVar, overload
from uuid import UUID

from server.eventbus.event import Event
from server.eventbus.interfaces import EventType
from server.managers.settings.interfaces import DefaultType
from server.managers.settings.models import SettingSchema
from server.webserver.models import WebSocketMessageData

if TYPE_CHECKING:
    from server.managers.components.base import Component

ClassType = TypeVar("ClassType", bound=object)
ReturnType = TypeVar("ReturnType", bound=object)


class PhotoboothAppInterface:
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
        self,
        event: type[EventType],
        listener: Callable[[EventType], None | Awaitable[None]],
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
        self,
        event: type[EventType],
        listener: Callable[[EventType], None | Awaitable[None]],
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
    def inject_constructor(
        self, cls: type[ClassType], named_deps: dict[str, object] = {}
    ) -> ClassType:
        """
        Inject dependencies into a class.

        Parameters
        ----------
        cls : type
            The class to inject dependencies into.
        named_deps : dict[str, object]
            Extra dependencies to inject based on the parameter name.

        Returns
        -------
        object
            The class with injected dependencies.
        """

    @abstractmethod
    async def call_with_injection(
        self, func: Callable[..., ReturnType], named_deps: dict[str, object] = {}
    ) -> ReturnType:
        """
        Call a function with dependency injection.

        Parameters
        ----------
        func : callable
            The function to call.
        named_deps : dict[str, object]
            Extra dependencies to inject based on the parameter name.

        Returns
        -------
        object
            The result of the function.
        """

    @abstractmethod
    def get_component(self, slug: str) -> Optional["Component"]:
        """
        Get a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to get.

        Returns
        -------
        Component | None
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
        self, source: str, schema: SettingSchema, sync: bool = True
    ) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        sync : bool
            Whether to sync the settings with the database, by default True.
        """

    @abstractmethod
    async def add_setting_schemas(
        self,
        source: str,
        schemas: list[SettingSchema],
        sync: bool = True,
    ) -> None:
        """
        Add a new settings schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schemas : list[SettingSchema]
            The schemas of the settings.
        sync : bool
            Whether to sync the settings with the database, by default True.
        """

    @abstractmethod
    def remove_setting_schema(self, source: str, key: str) -> None:
        """
        Remove a setting schema from the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        key : str
            The key of the setting.
        """

    @abstractmethod
    def remove_setting_schemas(self, source: str, keys: list[str]) -> None:
        """
        Remove setting schemas from the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        keys : list[str]
            The keys of the settings.
        """

    @overload
    @abstractmethod
    def get_setting_value(
        self, *, uuid: str | UUID, default: DefaultType | None = None
    ) -> object | DefaultType | None:
        """
        Get a setting value by its UUID.

        Parameters
        ----------
        uuid : str | UUID
            The UUID of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given UUID or the default value if it does not exist.
        """

    @overload
    @abstractmethod
    def get_setting_value(
        self, *, source: str, key: str, default: DefaultType | None = None
    ) -> object | DefaultType | None:
        """
        Get a setting value by its source and key.

        Parameters
        ----------
        source : str
            The source of the setting.
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
    def get_setting_value(
        self,
        *,
        uuid: str | UUID | None = None,
        source: str | None = None,
        key: str | None = None,
        default: DefaultType | None = None,
    ) -> object | DefaultType | None:
        """
        Get a setting value by its UUID or source and key.

        Parameters
        ----------
        uuid : str | UUID | None
            The UUID of the setting.
        source : str | None
            The source of the setting.
        key : str | None
            The key of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given UUID or source and key or the default value if it does not exist.
        """

    @abstractmethod
    def broadcast(self, channel: str, payload: WebSocketMessageData) -> None:
        """
        Broadcast a message to a channel to all subscribed clients via WebSocket.

        Parameters
        ----------
        channel : str
            The channel to broadcast to.
        payload : WebSocketMessageData
            The payload to broadcast.
        """
