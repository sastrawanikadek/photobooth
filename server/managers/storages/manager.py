from server.constants import SETTING_STORAGE_PROVIDER
from server.managers.settings.interfaces import SettingsManagerInterface

from .interfaces import StorageManagerInterface, StorageProviderInterface


class StorageManager(StorageManagerInterface):
    """Implementation of the storage manager."""

    _providers: dict[str, StorageProviderInterface] = {}

    def __init__(self, settings_manager: "SettingsManagerInterface") -> None:
        """
        Initialize the storage manager.

        Parameters
        ----------
        settings_manager : SettingsManagerInterface
            The settings manager.
        """
        self._settings_manager = settings_manager

    def add_provider(self, name: str, provider: StorageProviderInterface) -> None:
        """
        Add a storage provider.

        Parameters
        ----------
        name : str
            The name of the storage provider.
        provider : StorageProviderInterface
            The storage provider to add.

        Raises
        ------
        ValueError
            If a storage provider with the same name already exists.
        """
        if name in self._providers:
            raise ValueError(f'Storage provider with name "{name}" already exists')

        self._providers[name] = provider

    def remove_provider(self, name: str) -> None:
        """
        Remove a storage provider.

        Parameters
        ----------
        name : str
            The name of the storage provider.
        """
        self._providers.pop(name, None)

    def provider(self, name: str) -> StorageProviderInterface | None:
        """
        Get a storage provider by its name.

        Parameters
        ----------
        name : str
            The name of the storage provider to get.

        Returns
        -------
        StorageProviderInterface | None
            The storage provider with the given name or None if not found.
        """
        return self._providers.get(name)

    @property
    def default(self) -> StorageProviderInterface:
        """
        Get the default storage provider based on the settings.

        Returns
        -------
        StorageProviderInterface
            The default storage provider.
        """
        default_provider = str(
            self._settings_manager.get_value(
                source="system",
                key=SETTING_STORAGE_PROVIDER,
                default="local",
            )
        )

        return self._providers[default_provider]
