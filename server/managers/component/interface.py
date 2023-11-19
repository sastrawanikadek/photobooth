from abc import ABC, abstractmethod
from pathlib import Path

from injector import DependencyInjectorInterface

from .model import ComponentManifest


class ComponentInterface(ABC):
    """Interface for component implementations."""


class ComponentManagerInterface(ABC):
    """
    Interface for component manager implementations.

    Attributes
    ----------
    components : dict[str, ComponentInterface]
        The components managed by the manager.
    components_data : dict[str, dict[str, object]]
        The data of the components managed by the manager.
    manifests : dict[str, ComponentManifest]
        The manifests of the components managed by the manager.
    path : Path
        The path to the directory containing the components.
    """

    components: dict[str, ComponentInterface]
    components_data: dict[str, dict[str, object]]
    manifests: dict[str, ComponentManifest]
    path: Path
    injector: DependencyInjectorInterface

    @abstractmethod
    def __init__(self, path: Path, injector: DependencyInjectorInterface) -> None:
        """
        Initialize the component manager.

        Parameters
        ----------
        path : str
            The path to the directory containing the components.
        injector : DependencyInjectorInterface
            The dependency injector to use for dependency injection.
        """

    @abstractmethod
    def load(self) -> None:
        """
        Load all the components in the path and inject the necessary dependencies into
        the components.
        """

    @abstractmethod
    def get(self, slug: str) -> ComponentInterface:
        """
        Get a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to get.

        Returns
        -------
        ComponentInterface
            The component with the given slug.
        """

    @abstractmethod
    def get_data(self, slug: str) -> dict[str, object]:
        """
        Get the data of a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component data to get.

        Returns
        -------
        dict[str, object]
            The data of the component with the given slug.
        """

    @abstractmethod
    def get_manifest(self, slug: str) -> ComponentManifest:
        """
        Get a component manifest by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component manifest to get.

        Returns
        -------
        ComponentManifest
            The component manifest with the given slug.
        """

    @abstractmethod
    def remove(self, slug: str) -> None:
        """
        Remove a component along with its manifest and data by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to remove.
        """
