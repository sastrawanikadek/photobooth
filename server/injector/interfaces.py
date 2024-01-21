from abc import ABC, abstractmethod
from typing import Callable, ContextManager, TypeVar

_CT = TypeVar("_CT")
_RT = TypeVar("_RT", bound=object)


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
    def add_temporary_container(self) -> ContextManager["DependencyContainerInterface"]:
        """
        Add a temporary dependency container to use for dependency injection.

        Returns
        -------
        ContextManager[DependencyContainerInterface]
            The temporary dependency container.
        """

    @abstractmethod
    def inject_constructor(self, cls: _CT) -> _CT:
        """
        Inject dependencies into a class.

        Parameters
        ----------
        cls : type
            The class to inject dependencies into.

        Returns
        -------
        type
            The class with injected dependencies.
        """

    @abstractmethod
    async def call_with_injection(self, func: Callable[..., _RT]) -> _RT:
        """
        Call a function with dependency injection.

        Parameters
        ----------
        func : callable
            The function to call.

        Returns
        -------
        _RT
            The result of the function.
        """


class DependencyContainerInterface(ABC):
    """
    Interface for dependency container implementations.

    A dependency container is a container for bindings between interfaces and implementations.
    """

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
    def bind(self, interface: type, implementation: type | Callable[[], type]) -> None:
        """
        Bind an interface to an implementation.

        Implementations are instantiated every time they are injected.

        Parameters
        ----------
        interface : type
            The interface to bind.
        implementation : type | Callable[[], type]
            The implementation to bind to the interface.
        """

    @abstractmethod
    def singleton(
        self, interface: type, implementation: type | Callable[[], type]
    ) -> None:
        """
        Bind an interface to a singleton implementation.

        Implementations are only instantiated once and then reused.

        Parameters
        ----------
        interface : type
            The interface to bind.
        implementation : type | Callable[[], type]
            The implementation to bind to the interface.
        """
