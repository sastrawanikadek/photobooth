import inspect
from contextlib import contextmanager
from typing import Callable, Iterator, cast

from utils.helpers.function import safe_invoke

from .dependency_container import DependencyContainer
from .interfaces import (
    _CT,
    _RT,
    DependencyContainerInterface,
    DependencyInjectorInterface,
)


class DependencyInjector(DependencyInjectorInterface):
    """Dependency injection implementation."""

    def __init__(self) -> None:
        """Initialize the dependency injector."""
        self.containers = []

    def add_container(self, container: DependencyContainerInterface) -> None:
        """
        Add a dependency container to use for dependency injection.

        Parameters
        ----------
        container : DependencyContainerInterface
            The dependency container to add.

        Examples
        --------
        >>> from injector import Injector, DependencyContainer
        >>> injector = Injector()
        >>> container = DependencyContainer()
        >>> injector.add_container(container)
        """
        self.containers.append(container)

    @contextmanager
    def add_temporary_container(self) -> Iterator[DependencyContainerInterface]:
        """
        Add a temporary dependency container to use for dependency injection.

        Returns
        -------
        ContextManager[DependencyContainerInterface]
            The temporary dependency container.

        Examples
        --------
        >>> from injector import Injector, DependencyContainer
        >>> injector = Injector()
        >>> with injector.add_temporary_container() as container:
        ...     pass
        """
        container = DependencyContainer()
        self.add_container(container)

        try:
            yield container
        finally:
            self.containers.remove(container)

    def inject_constructor(self, cls: _CT) -> _CT:
        """
        Inject dependencies into a class using the constructor.

        Parameters
        ----------
        cls : type
            The class to inject dependencies into.

        Returns
        -------
        type
            The instance of the class with dependencies injected.

        Raises
        ------
        TypeError
            If the class is not a class.

        Examples
        --------
        >>> from injector import Injector, DependencyContainer
        >>> injector = Injector()
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.bind(Interface, Implementation)
        >>> injector.add_container(container)
        >>> class Test:
        ...     def __init__(self, interface: Interface):
        ...         self.interface = interface
        ...
        >>> injector.inject_constructor(Test)
        <__main__.Test object at 0x7f5d6f9b6f10>
        """
        if not inspect.isclass(cls):
            raise TypeError(f"{cls} is not a class")

        signature = inspect.signature(cls.__init__)
        args = []

        for parameter in signature.parameters.values():
            if parameter.annotation == parameter.empty:
                continue

            for container in self.containers:
                try:
                    dependency = container.get(parameter.annotation)
                    args.append(dependency)
                    break
                except TypeError:
                    continue

        instance = cls(*args)
        return cast(_CT, instance)

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

        Examples
        --------
        >>> from injector import Injector, DependencyContainer
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> def test(interface: Interface):
        ...     return interface
        >>> async def main() -> None:
        ...     injector = Injector()
        ...     container = DependencyContainer()
        ...     container.bind(Interface, Implementation)
        ...     injector.add_container(container)
        ...     await injector.call_with_injection(test)
        <__main__.Implementation object at 0x7f5d6f9b6f10>
        """
        signature = inspect.signature(func)
        args = []

        for parameter in signature.parameters.values():
            if parameter.annotation == parameter.empty:
                continue

            for container in self.containers:
                try:
                    dependency = container.get(parameter.annotation)
                    args.append(dependency)
                    break
                except TypeError:
                    continue

        return cast(_RT, await safe_invoke(func, *args))
