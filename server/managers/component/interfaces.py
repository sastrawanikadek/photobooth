from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from injector import DependencyInjectorInterface

from .model import ComponentManifest


class ComponentInterface(ABC):
    """Interface for all components."""


class ComponentManagerInterface(ABC):
    """Interface for component manager implementations."""

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
    def load_preinstalled(self) -> None:
        """
        Load all the preinstalled components in the path and inject the necessary dependencies into
        the components.
        """

    @abstractmethod
    def get(self, slug: str) -> Optional[ComponentInterface]:
        """
        Get a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to get.

        Returns
        -------
        Optional[ComponentInterface]
            The component with the given slug or None if not installed.
        """

    @abstractmethod
    def get_data(self, slug: str) -> Optional[dict[str, object]]:
        """
        Get the data of a component by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component data to get.

        Returns
        -------
        Optional[dict[str, object]]
            The data of the component with the given slug or None if component is not installed.
        """

    @abstractmethod
    def get_manifest(self, slug: str) -> Optional[ComponentManifest]:
        """
        Get a component manifest by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component manifest to get.

        Returns
        -------
        Optional[ComponentManifest]
            The component manifest with the given slug or None if component is not installed.
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
