from .interfaces import DependencyContainerInterface


class DependencyContainer(DependencyContainerInterface):
    """
    Dependency container implementation.

    This class provides a central interface for managing dependencies.

    Attributes
    ----------
    _bindings : dict[type, type]
        A dictionary of bindings, keyed by interface.
    """

    _bindings: dict[type, type]

    def __init__(self) -> None:
        """Initialize the dependency container."""
        self._bindings = {}

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
        if interface not in self._bindings:
            raise TypeError(f"no binding for {interface}")

        return self._bindings[interface]

    def bind(self, interface: type, implementation: type) -> None:
        """
        Bind an interface to an implementation.

        Parameters
        ----------
        interface : type
            The interface to bind.
        implementation : type
            The implementation to bind to the interface.

        Raises
        ------
        TypeError
            If the implementation is not a subclass of the interface.

        Examples
        --------
        >>> from injector import DependencyContainer
        >>> container = DependencyContainer()
        >>> class Interface: pass
        >>> class Implementation(Interface): pass
        >>> container.bind(Interface, Implementation)
        """
        if not issubclass(type(implementation), interface):
            raise TypeError(f"{implementation} is not a subclass of {interface}")

        self._bindings[interface] = implementation
