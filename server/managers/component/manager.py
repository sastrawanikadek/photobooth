import json
import os
from pathlib import Path
from typing import Optional

from injector import DependencyInjectorInterface
from utils.helpers.module import get_module_class, import_module_by_path

from .interface import ComponentInterface, ComponentManagerInterface
from .model import ComponentManifest


class ComponentManager(ComponentManagerInterface):
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
        self.components = {}
        self.components_data = {}
        self.manifests = {}
        self.path = path
        self.injector = injector

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

        component: ComponentInterface = self.injector.inject_constructor(component_cls)
        return component

    def load(self) -> None:
        """
        Load the components.

        Parameters
        ----------
        injector : DependencyInjectorInterface
            The dependency injector to use for dependency injection.
        """
        for component_name in os.listdir(self.path):
            component_path = self.path / component_name
            manifest = self._load_manifest(component_path)

            if manifest is None:
                continue

            component = self._load_component(component_path, manifest)

            if component is None:
                continue

            self.components[manifest.slug] = component
            self.components_data[manifest.slug] = {}
            self.manifests[manifest.slug] = manifest

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
        return self.components[slug]

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
        return self.components_data[slug]

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
        return self.manifests[slug]

    def remove(self, slug: str) -> None:
        """
        Remove a component and its manifest by its slug.

        Parameters
        ----------
        slug : str
            The slug of the component to remove.
        """
        del self.components[slug]
