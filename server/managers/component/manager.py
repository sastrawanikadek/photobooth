import json
import logging
from pathlib import Path
from typing import Optional

from injector import DependencyInjectorInterface
from utils.helpers.module import get_module_class, import_module_by_path

from .interfaces import ComponentInterface, ComponentManagerInterface
from .model import ComponentManifest

_LOGGER = logging.getLogger(__name__)


class ComponentManager(ComponentManagerInterface):
    """
    Implementation of the component manager.

    Attributes
    ----------
    _components : dict[str, ComponentInterface]
        The components managed by the manager.
    _components_data : dict[str, dict[str, object]]
        The data of the components managed by the manager.
    _manifests : dict[str, ComponentManifest]
        The manifests of the components managed by the manager.
    _path : Path
        The path to the directory containing the components.
    _injector : DependencyInjectorInterface
        The dependency injector to use for dependency injection.
    """

    _components: dict[str, ComponentInterface]
    _components_data: dict[str, dict[str, object]]
    _manifests: dict[str, ComponentManifest]
    _path: Path
    _injector: DependencyInjectorInterface

    def __init__(self, path: Path, injector: DependencyInjectorInterface) -> None:
        """
        Initialize the component manager.

        Parameters
        ----------
        path : Path
            The path to the directory containing the components.
        injector : DependencyInjectorInterface
            The dependency injector to use for dependency injection.
        """
        self._components = {}
        self._components_data = {}
        self._manifests = {}
        self._path = path
        self._injector = injector

    def _load_manifest(self, component_path: Path) -> Optional[ComponentManifest]:
        """
        Load a component manifest.

        Parameters
        ----------
        component_path : Path
            The path to the component.

        Returns
        -------
        Optional[ComponentManifest]
            The manifest of the component.
        """
        manifest_path = component_path / "manifest.json"

        if not manifest_path.exists():
            return None

        manifest_data = json.load(open(manifest_path))
        return ComponentManifest(**manifest_data)

    def _load_component(
        self, component_path: Path, manifest: ComponentManifest
    ) -> Optional[ComponentInterface]:
        """
        Load a component.

        Parameters
        ----------
        component_path : Path
            The path to the component.
        manifest : ComponentManifest
            The manifest of the component.

        Returns
        -------
        Optional[ComponentInterface]
            The component.
        """
        module = import_module_by_path(component_path)

        if module is None:
            return None

        component_cls = get_module_class(module, manifest.name, ComponentInterface)

        if component_cls is None:
            return None

        component: ComponentInterface = self._injector.inject_constructor(component_cls)
        return component

    def load_preinstalled(self) -> None:
        """
        Load all the preinstalled components in the path and inject the necessary dependencies into
        the components.

        Parameters
        ----------
        injector : DependencyInjectorInterface
            The dependency injector to use for dependency injection.
        """
        component_paths = sorted(
            [
                component_path
                for component_path in self._path.iterdir()
                if component_path.is_dir()
            ],
            key=lambda x: x.name,
        )

        for component_path in component_paths:
            manifest = self._load_manifest(component_path)

            if manifest is None or not manifest.preinstalled:
                continue

            _LOGGER.debug("Loading component %s", manifest.display_name)

            component = self._load_component(component_path, manifest)

            if component is None:
                continue

            self._components[manifest.slug] = component
            self._components_data[manifest.slug] = {}
            self._manifests[manifest.slug] = manifest

            _LOGGER.info("Loaded component %s", manifest.display_name)

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
        return self._components.get(slug)

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
        return self._components_data.get(slug)

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
        return self._manifests.get(slug)

    def remove(self, slug: str) -> None:
        """
        Remove a component and its manifest by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to remove.
        """
        try:
            del self._components[slug]
        except KeyError:
            _LOGGER.warning(
                "Tried to remove component %s, but it was not installed.", slug
            )
