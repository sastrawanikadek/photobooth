import asyncio
import logging

from server.constants import COMPONENTS_PATH, DATABASE_CONNECTION_STRING
from server.database import DatabaseInterface, SQLiteDatabase
from server.eventbus import EventBus, EventBusInterface
from server.injector import (
    DependencyContainer,
    DependencyContainerInterface,
    DependencyInjector,
    DependencyInjectorInterface,
)
from server.managers.component import ComponentManager, ComponentManagerInterface
from server.managers.settings import SettingsManager, SettingsManagerInterface
from server.websocket import WebSocket, WebSocketInterface

from .events import AppInitializedEvent, AppReadyEvent, AppStartupEvent
from .interfaces import PhotoboothInterface
from .providers import DEFAULT_PROVIDERS, ServiceProviderInterface
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
    """

    _providers: list[ServiceProviderInterface] = []

    def __init__(self) -> None:
        self.eventbus = EventBus()
        self.database = SQLiteDatabase(DATABASE_CONNECTION_STRING)
        self.dependency_container = DependencyContainer()
        self.dependency_injector = DependencyInjector([self.dependency_container])
        self.component_manager = ComponentManager(
            COMPONENTS_PATH, self.dependency_injector
        )
        self.websocket = WebSocket(self.dependency_injector)

    def initialize(self) -> None:
        """
        Bootstrap the photobooth.

        Initialize the main components of the photobooth.
        """
        self._register_core_dependencies()
        self._register_providers(DEFAULT_PROVIDERS)

        self.settings_manager = self.dependency_injector.inject_constructor(
            SettingsManager
        )
        self.dependency_container.singleton(
            SettingsManagerInterface, self.settings_manager
        )

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
        self._load_settings()

        # Invoke the boot method of the service providers
        injected_boot_methods = [
            self.dependency_injector.call_with_injection(provider.boot)
            for provider in self._providers
        ]
        await asyncio.gather(*injected_boot_methods)

        # Start the websocket server
        asyncio.create_task(self.websocket.start())

        # Set the app proxy
        set_photobooth(PhotoboothApp(self))

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
            WebSocketInterface: self.websocket,
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
        self, providers: list[type[ServiceProviderInterface]]
    ) -> None:
        """
        Register the service providers.

        Parameters
        ----------
        providers : list[type[ServiceProviderInterface]]
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

            # Register websocket routes
            for route in instance.websocket_routes:
                self.websocket.add_handler(*route)

            # Invoke provider register method
            instance.register()

            self._providers.append(instance)

    def _load_preinstalled_components(self) -> None:
        """Load all the preinstalled components."""
        _LOGGER.info("Loading preinstalled components")

        self.component_manager.load_preinstalled()
        manifests = self.component_manager.get_all_manifests()

        # Register components providers
        providers = [
            provider for manifest in manifests for provider in manifest.providers
        ]
        self._register_providers(providers)

        _LOGGER.info("Preinstalled components loaded")

    def _load_settings(self) -> None:
        """
        Load the settings from different sources to
        the settings manager.
        """
        _LOGGER.info("Loading settings")

        manifests = self.component_manager.get_all_manifests()
        schemas = {manifest.slug: manifest.settings for manifest in manifests}

        for provider in self._providers:
            schemas.update(provider.setting_schemas)

        asyncio.create_task(self.settings_manager.load(schemas))

        _LOGGER.info("Settings loaded")
