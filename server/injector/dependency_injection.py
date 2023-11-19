import inspect
from typing import cast

from .interface import (
    _CT,
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
        >>> from injector import Injector, AppDependencyContainer
        >>> injector = Injector()
        >>> container = AppDependencyContainer()
        >>> injector.add_container(container)
        """
        self.containers.append(container)

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
        >>> from injector import Injector, AppDependencyContainer
        >>> injector = Injector()
        >>> container = AppDependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.bind(Interface, Implementation)
        >>> injector.add_container(container)
        >>> class Test:
        ...     def __init__(self, interface: Interface):
        ...         self.interface = interface
        ...
        >>> test = injector.inject(Test)
        >>> test.interface
        <class '__main__.Implementation'>
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
