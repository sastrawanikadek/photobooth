from constants import COMPONENTS_PATH
from eventbus import EventBus, EventBusInterface
from injector import DependencyContainer, DependencyInjector
from injector.interfaces import DependencyInjectorInterface
from interfaces import PhotoboothInterface
from managers.component import ComponentManager, ComponentManagerInterface


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

    def __init__(self) -> None:
        self.eventbus = EventBus()
        self.dependency_container = DependencyContainer()
        self.dependency_injector = DependencyInjector()
        self.component_manager = ComponentManager(
            COMPONENTS_PATH, self.dependency_injector
        )

        self.dependency_container.bind(EventBusInterface, self.eventbus)
        self.dependency_container.bind(
            ComponentManagerInterface, self.component_manager
        )
        self.dependency_container.bind(
            DependencyInjectorInterface, self.dependency_injector
        )

        self.dependency_injector.add_container(self.dependency_container)
