import inspect
from typing import Callable, cast

from .interfaces import DependencyContainerInterface


class DependencyContainer(DependencyContainerInterface):
    """
    Dependency container implementation.

    This class provides a central interface for managing dependencies.

    Attributes
    ----------
    _bindings : dict[type, type]
        A dictionary of bindings, keyed by interface.
    _singletons : dict[type, type]
        A dictionary of singletons, keyed by interface.
    """

    _bindings: dict[type, type | Callable[[], type]] = {}
    _singletons: dict[type, type] = {}

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

        Raises
        ------
        TypeError
            If there is no binding for the interface.

        Examples
        --------
        >>> from injector import DependencyContainer
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.bind(Interface, Implementation)
        >>> container.get(Interface)
        <class '__main__.Implementation'>
        """
        if interface in self._singletons:
            return self._singletons[interface]
        elif interface in self._bindings and callable(self._bindings[interface]):
            return self._bindings[interface]()
        elif interface in self._bindings:
            return cast(type, self._bindings[interface])

        raise TypeError(f'No binding for "{interface}"')

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
        elif not issubclass(type(implementation), interface):
            raise TypeError(f'"{implementation}" is not a subclass of "{interface}"')
        elif not inspect.isclass(implementation) and not callable(implementation):
            raise TypeError(f'"{implementation}" is not a class')

        if callable(implementation) and not issubclass(
            type(implementation()), interface
        ):
            raise TypeError(f'"{implementation}" is not a subclass of "{interface}"')

        self._bindings[interface] = implementation

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

        if interface in self._bindings:
            raise ValueError(f'"{interface}" is already bound as a dependency')
        elif inspect.isclass(implementation) and not callable(implementation):
            raise TypeError(f'"{implementation}" is not an instance')
        elif not issubclass(type(implementation), interface):
            raise TypeError(f'"{implementation}" is not a subclass of "{interface}"')

        if callable(implementation):
            instance = implementation()

            if not issubclass(type(instance), interface):
                raise TypeError(
                    f'"{implementation}" is not a subclass of "{interface}"'
                )

            self._singletons[interface] = instance
        else:
            self._singletons[interface] = implementation
