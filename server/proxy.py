from typing import Awaitable, Callable

from server.eventbus import Event
from server.managers.component import ComponentInterface
from server.managers.settings import SettingSchema

from .interfaces import (
    PhotoboothAppInterface,
    PhotoboothInterface,
    TClass,
    TDefault,
    TEvent,
    TReturn,
)


class PhotoboothApp(PhotoboothAppInterface):
    """The photobooth app."""

    def __init__(self, photobooth: PhotoboothInterface) -> None:
        self._photobooth = photobooth

    def dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered listeners.

        Parameters
        ----------
        event : Event
            The event to dispatch.
        """
        self._photobooth.eventbus.dispatch(event)

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
        self._photobooth.eventbus.add_listener(event, listener)

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
        self._photobooth.eventbus.remove_listener(event, listener)

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
        self._photobooth.dependency_container.bind(interface, implementation)

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
        self._photobooth.dependency_container.singleton(interface, implementation)

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
        container = self._photobooth.dependency_container
        instance = container.get_singleton(interface)

        if instance is not None:
            return instance

        implementation = container.get_bind(interface)

        if implementation is None:
            raise ValueError(f'Could not resolve implementation for "{interface}"')
        elif callable(implementation):
            injector = self._photobooth.dependency_injector
            args = injector.resolve_dependencies(implementation)
            instance = implementation(*args)
            return instance

        return self._photobooth.dependency_injector.inject_constructor(implementation)

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
        return self._photobooth.dependency_injector.inject_constructor(cls)

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
        return await self._photobooth.dependency_injector.call_with_injection(func)

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
        return self._photobooth.component_manager.get(slug)

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
        return self._photobooth.component_manager.get_data(slug)

    def add_setting_schema(self, source: str, schema: SettingSchema) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        """
        self._photobooth.settings_manager.add_schema(source, schema)

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
        return self._photobooth.settings_manager.get_value(source, key, default)

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
        self._photobooth.settings_manager.set_value(source, key, value)


_photobooth: PhotoboothAppInterface | None = None


def set_photobooth(photobooth: PhotoboothAppInterface) -> None:
    """Set the photobooth."""
    global _photobooth
    _photobooth = photobooth


def app() -> PhotoboothAppInterface:
    """Get the photobooth app instance."""
    if _photobooth is None:
        raise RuntimeError("Photobooth not set")

    return _photobooth
