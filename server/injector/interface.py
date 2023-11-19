from abc import ABC, abstractmethod
from typing import TypeVar

_CT = TypeVar("_CT", bound=type)


class DependencyInjectorInterface(ABC):
    """
    Interface for dependency injection implementations.

    Dependency injection is the process of injecting dependencies into a class.

    Attributes
    ----------
    containers : list[DependencyContainerInterface]
        The dependency containers to use for dependency injection.
    """

    containers: list["DependencyContainerInterface"]

    @abstractmethod
    def add_container(self, container: "DependencyContainerInterface") -> None:
        """
        Add a dependency container to use for dependency injection.

        Parameters
        ----------
        container : DependencyContainerInterface
            The dependency container to add.
        """

    @abstractmethod
    def inject_constructor(self, cls: _CT) -> _CT:
        """
        Inject dependencies into a class.

        Parameters
        ----------
        cls : type
            The class to inject dependencies into.
        """


class DependencyContainerInterface(ABC):
    """
    Interface for dependency container implementations.

    A dependency container is a container for bindings between interfaces and implementations.

    Attributes
    ----------
    bindings : dict[type, type]
        The bindings between interfaces and implementations.
    """

    bindings: dict[type, type]

    @abstractmethod
    def get(self, interface: type) -> type:
        """
        Get an implementation for an interface.

        Parameters
        ----------
        interface : type
            The interface to get an implementation for.

        Returns
        -------
        type
            The implementation for the interface.
        """

    @abstractmethod
    def bind(self, interface: type, implementation: type) -> None:
        """
        Bind an interface to an implementation.

        Parameters
        ----------
        interface : type
            The interface to bind.
        implementation : type
            The implementation to bind to the interface.
        """
