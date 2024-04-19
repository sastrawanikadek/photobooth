import asyncio
import logging

from server.constants import COMPONENTS_PATH, DATABASE_CONNECTION_STRING
from server.database.interfaces import DatabaseInterface
from server.database.sqlite import SQLiteDatabase
from server.dependency_injection.dependency_container import DependencyContainer
from server.dependency_injection.dependency_injector import DependencyInjector
from server.dependency_injection.interfaces import (
    DependencyContainerInterface,
    DependencyInjectorInterface,
)
from server.eventbus.bus import EventBus
from server.eventbus.interfaces import EventBusInterface
from server.managers.components.interfaces import ComponentManagerInterface
from server.managers.components.manager import ComponentManager
from server.managers.settings.interfaces import SettingsManagerInterface
from server.managers.settings.manager import SettingsManager
from server.managers.storages.constants import (
    DEFAULT_PROVIDERS as DEFAULT_STORAGE_PROVIDERS,
)
from server.managers.storages.interfaces import (
    StorageManagerInterface,
    StorageProviderInterface,
)
from server.managers.storages.manager import StorageManager
from server.utils.pydantic_fields.string import SlugStr
from server.webserver.interfaces import WebServerInterface
from server.webserver.server import WebServer

from .events import AppInitializedEvent, AppReadyEvent, AppStartupEvent
from .interfaces import PhotoboothInterface
from .providers import DEFAULT_PROVIDERS, ServiceProvider
from .proxy import PhotoboothApp, set_photobooth

_LOGGER = logging.getLogger(__name__)


class Photobooth(PhotoboothInterface):
    """
    The core class of the photobooth.

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

    _providers: dict[str, list[ServiceProvider]] = {}

    def __init__(self) -> None:
        self.eventbus = EventBus()
        self.database = SQLiteDatabase(DATABASE_CONNECTION_STRING)
        self.dependency_container = DependencyContainer()
        self.dependency_injector = DependencyInjector([self.dependency_container])
        self.component_manager = ComponentManager(
            COMPONENTS_PATH, self.dependency_injector
        )
        self.webserver = WebServer(self.dependency_injector)

    def initialize(self) -> None:
        """
        Bootstrap the photobooth.

        Initialize the main components of the photobooth.
        """
        self._register_core_dependencies()
        self._register_providers("system", DEFAULT_PROVIDERS)

        self.settings_manager = self.dependency_injector.inject_constructor(
            SettingsManager
        )
        self.dependency_container.singleton(
            SettingsManagerInterface, self.settings_manager
        )

        self.storage_manager = StorageManager(self.settings_manager)
        self.dependency_container.singleton(
            StorageManagerInterface, self.storage_manager
        )
        self._register_storage_providers(DEFAULT_STORAGE_PROVIDERS)

        _LOGGER.info("App initialized")
        self.eventbus.dispatch(AppInitializedEvent())

    def prepare(self) -> None:
        """
        Prepare the photobooth.

        Load all the necessary components and providers.
        """
        self._load_preinstalled_components()

        _LOGGER.info("App starting up")
        self.eventbus.dispatch(AppStartupEvent())

    async def startup(self) -> None:
        """
        Start the photobooth.

        Load all the settings and start necessary services.
        """
        await self._load_settings()
        await self._boot_providers()
        await self.settings_manager.sync()

        # Start the webserver
        await self.webserver.start()

        # Set the app proxy
        set_photobooth(PhotoboothApp(self))  # type: ignore[abstract]

        _LOGGER.info("App ready")
        self.eventbus.dispatch(AppReadyEvent())

        await asyncio.Future()

    def _register_core_dependencies(self) -> None:
        """Register the core dependencies in the dependency container."""
        dependencies = {
            EventBusInterface: self.eventbus,
            DatabaseInterface: self.database,
            DependencyContainerInterface: self.dependency_container,
            DependencyInjectorInterface: self.dependency_injector,
            ComponentManagerInterface: self.component_manager,
            WebServerInterface: self.webserver,
        }

        for interface, instance in dependencies.items():
            self.dependency_container.singleton(interface, instance)

    def _register_dependencies(
        self, dependencies: dict[type, type], singleton: bool = False
    ) -> None:
        """
        Register the dependencies in the dependency container.

        Parameters
        ----------
        dependencies : dict[type, type]
            The dependencies to register.
        singleton : bool
            Whether the dependencies should be registered as singletons,
            by default False.
        """
        queues = list(dependencies.items())
        failed = []

        attempt = 0
        max_attempt = 3

        while len(queues) > 0:
            interface, implementation = queues.pop(0)
            resolved = True

            try:
                instance: object = self.dependency_injector.inject_constructor(
                    implementation
                )
                attempt = 0
            except ValueError:
                failed.append((interface, implementation))
                resolved = False

            if len(queues) == 0:
                attempt += 1

                if attempt > max_attempt:
                    _LOGGER.warning(f"Failed to register dependencies: {queues}")
                    break

                queues = failed
                failed = []

            if not resolved:
                continue

            if singleton:
                self.dependency_container.singleton(interface, instance)
            else:
                self.dependency_container.bind(interface, implementation)

    def _register_providers(
        self, source: SlugStr, providers: list[type[ServiceProvider]]
    ) -> None:
        """
        Register the service providers.

        Parameters
        ----------
        source : SlugStr
            The source of the service providers, it can be either a component slug
            or "system".
        providers : list[type[ServiceProvider]]
            The service providers to register.
        """
        for provider in providers:
            instance = provider(
                self.dependency_container,
                self.eventbus,
            )

            # Register the dependencies of the service provider.
            self._register_dependencies(instance.dependencies)
            self._register_dependencies(instance.singletons, singleton=True)

            # Register API routes
            for route in instance.routes:
                if route.method is not None and route.http_handler is not None:
                    self.webserver.http.add_route(
                        route.method, route.endpoint, route.http_handler, **route.kwargs
                    )
                elif route.is_websocket and route.websocket_handler is not None:
                    self.webserver.websocket.add_handler(
                        route.endpoint, route.websocket_handler
                    )
                elif route.cls is not None and route.cls_method_name is not None:
                    if route.method is not None:
                        self.webserver.http.add_route(
                            route.method,
                            route.endpoint,
                            route.cls,
                            route.cls_method_name,
                            **route.kwargs,
                        )
                    elif route.is_websocket:
                        self.webserver.websocket.add_handler(
                            route.endpoint, route.cls, route.cls_method_name
                        )

            # Register websocket channels
            self.webserver.websocket.add_channels(instance.channels)

            # Invoke provider register method
            instance.register()

            self._providers.setdefault(source, [])
            self._providers[source].append(instance)

    async def _boot_providers(self) -> None:
        """Invoke the boot method of the service providers."""
        injected_boot_methods = [
            self.dependency_injector.call_with_injection(provider.boot)
            for providers in self._providers.values()
            for provider in providers
        ]
        await asyncio.gather(*injected_boot_methods)

    def _load_preinstalled_components(self) -> None:
        """Load all the preinstalled components."""
        _LOGGER.info("Loading preinstalled components")

        self.component_manager.load_preinstalled()
        manifests = self.component_manager.get_all_manifests()

        # Register components providers
        for manifest in manifests:
            self._register_providers(manifest.slug, manifest.providers)

        _LOGGER.info("Preinstalled components loaded")

    async def _load_settings(self) -> None:
        """
        Load the settings from different sources to
        the settings manager.
        """
        _LOGGER.info("Loading settings")

        manifests = self.component_manager.get_all_manifests()
        coroutines = []

        for manifest in manifests:
            coroutines.append(
                self.settings_manager.add_schemas(
                    manifest.slug, manifest.settings, sync=False
                )
            )

        for source, providers in self._providers.items():
            for provider in providers:
                coroutines.append(
                    self.settings_manager.add_schemas(
                        source, provider.setting_schemas, sync=False
                    )
                )

        await asyncio.gather(*coroutines)

        _LOGGER.info("Settings loaded")

    def _register_storage_providers(
        self, providers: dict[str, type[StorageProviderInterface]]
    ) -> None:
        """Register the storage providers."""
        for name, provider_cls in providers.items():
            provider = self.dependency_injector.inject_constructor(provider_cls)
            self.storage_manager.add_provider(name, provider)
