from abc import ABC

from eventbus import EventBusInterface
from injector import DependencyContainerInterface, DependencyInjectorInterface
from managers.component import ComponentManagerInterface


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
    """

    component_manager: ComponentManagerInterface
    dependency_container: DependencyContainerInterface
    dependency_injector: DependencyInjectorInterface
    eventbus: EventBusInterface
