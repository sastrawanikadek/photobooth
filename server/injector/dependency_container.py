import inspect
from typing import Callable

from .interfaces import DependencyContainerInterface


class DependencyContainer(DependencyContainerInterface):
    """
    Dependency container implementation.

    This class provides a central interface for managing dependencies.

    Attributes
    ----------
    _bindings : dict[type, type | Callable[..., object]]
        A dictionary of bindings, keyed by interface.
    _singletons : dict[type, object]
        A dictionary of singletons, keyed by interface.
    """

    _bindings: dict[type, type | Callable[..., object]] = {}
    _singletons: dict[type, object] = {}

    def get_bind(self, interface: type) -> type | Callable[..., object] | None:
        """
        Get an implementation for an interface.

        Parameters
        ----------
        interface : type
            The interface to get an implementation for.

        Returns
        -------
        type | Callable[..., object] | None
            The implementation or the factory for the interface or
            None if there is no binding.

        Examples
        --------
        >>> from injector import DependencyContainer
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.bind(Interface, Implementation)
        >>> container.get_bind(Interface)
        <class '__main__.Implementation'>
        """
        return self._bindings.get(interface, None)

    def get_singleton(self, interface: type) -> object | None:
        """
        Get a singleton implementation for an interface.

        Parameters
        ----------
        interface : type
            The interface to get an implementation for.

        Returns
        -------
        object | None
            The singleton instance for the interface or
            None if there is no singleton.

        Examples
        --------
        >>> from injector import DependencyContainer
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.singleton(Interface, Implementation())
        >>> container.get_singleton(Interface)
        <Implementation object at 0x7f9f0a7b9a30>
        """
        return self._singletons.get(interface, None)

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

        Raises
        ------
        ValueError
            If the interface is already bound as a singleton.
        TypeError
            If the implementation is not a subclass of the interface or
            if the implementation is not a class.

        Examples
        --------
        >>> from injector import DependencyContainer
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.bind(Interface, Implementation)
        """
        if interface in self._singletons:
            raise ValueError(f'"{interface}" is already bound as a singleton')
        elif not callable(implementation) and not inspect.isclass(implementation):
            raise TypeError(f'"{implementation}" is not a class')
        elif not callable(implementation) and not issubclass(implementation, interface):
            raise TypeError(f'"{implementation}" is not a subclass of "{interface}"')

        if callable(implementation):
            return_type = inspect.signature(implementation).return_annotation

            if not inspect.isclass(return_type):
                raise TypeError(f'"{return_type}" is not a class')
            elif not issubclass(return_type, interface):
                raise TypeError(f'"{return_type}" is not a subclass of "{interface}"')

        self._bindings[interface] = implementation

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
            The implementation to bind to the interface.

        Raises
        ------
        ValueError
            If the interface is already bound as a dependency.
        TypeError
            If the implementation is not an instance or factory.
            If the implementation is not a subclass of the interface.

        Examples
        --------
        >>> from injector import DependencyContainer
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.singleton(Interface, Implementation)
        """

        if interface in self._bindings:
            raise ValueError(f'"{interface}" is already bound as a dependency')
        elif not callable(implementation) and inspect.isclass(implementation):
            raise TypeError(f'"{implementation}" is not an instance')
        elif not callable(implementation) and not issubclass(
            type(implementation), interface
        ):
            raise TypeError(f'"{implementation}" is not a subclass of "{interface}"')

        if callable(implementation):
            instance = implementation()

            if not issubclass(type(instance), interface):
                raise TypeError(f'"{instance}" is not a subclass of "{interface}"')

            self._singletons[interface] = instance
        else:
            self._singletons[interface] = implementation
