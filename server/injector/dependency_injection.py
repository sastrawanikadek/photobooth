import inspect
from contextlib import contextmanager
from typing import Callable, Iterator, cast

from server.utils.helpers.function import safe_invoke
from server.utils.helpers.inspect import has_no_parameters, is_builtin_type

from .dependency_container import DependencyContainer
from .interfaces import (
    _CT,
    _RT,
    DependencyContainerInterface,
    DependencyInjectorInterface,
)


class DependencyInjector(DependencyInjectorInterface):
    """Dependency injection implementation."""

    def __init__(self, containers: list[DependencyContainerInterface] = []) -> None:
        """Initialize the dependency injector."""
        self.containers = containers

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

    def resolve_dependencies(self, func: Callable[..., object]) -> list[object]:
        """
        Resolve the dependencies for a function.

        Parameters
        ----------
        func : callable
            The function to resolve dependencies for.

        Returns
        -------
        list[object]
            The resolved dependencies.

        Raises
        ------
        TypeError
            If a dependency could not be resolved.
        """
        signature = inspect.signature(func)
        args: list[object] = []

        for parameter in signature.parameters.values():
            if parameter.annotation == parameter.empty:
                continue

            if is_builtin_type(parameter.annotation):
                raise ValueError(
                    f'Could not resolve dependency for "{parameter.annotation}"'
                )

            dependency = self._resolve_dependency(parameter.annotation)

            if dependency is not None:
                args.append(dependency)
                continue

            if not has_no_parameters(parameter.annotation):
                raise ValueError(
                    f'Could not resolve dependency for "{parameter.annotation}"'
                )

            # Instantiating the dependency if it is a class and has no parameters.
            args.append(parameter.annotation())

        return args

    def inject_constructor(self, cls: type[_CT]) -> _CT:
        """
        Inject dependencies into a class using the constructor.

        Parameters
        ----------
        cls : type
            The class to inject dependencies into.

        Returns
        -------
        object
            The instance of the class with dependencies injected.

        Raises
        ------
        TypeError
            If the class is not a class.
        ValueError
            If a dependency could not be resolved.

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
            raise TypeError(f'"{cls}" is not a class')

        args = self.resolve_dependencies(cls.__init__)
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
        object
            The result of the function.

        Raises
        ------
        ValueError
            If a dependency could not be resolved.

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
        args = self.resolve_dependencies(func)
        return cast(_RT, await safe_invoke(func, *args))

    def _resolve_dependency(self, annotation: type) -> object | None:
        """
        Resolve a dependency by looking through the dependency containers.

        Parameters
        ----------
        annotation : type
            The annotation to resolve.

        Returns
        -------
        object | None
            The resolved dependency or None if it could not be resolved.
        """
        for container in self.containers:
            dependency = container.get_singleton(annotation)

            if dependency is not None:
                return dependency

            implementation = container.get_bind(annotation)

            if implementation is None:
                continue

            try:
                dependency_args = self.resolve_dependencies(implementation)
            except ValueError:
                break
            else:
                dependency = implementation(*dependency_args)
                return dependency

        return None
