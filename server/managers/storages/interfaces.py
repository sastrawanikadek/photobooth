from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class StorageProviderInterface(ABC):
    """Interface for storage providers."""

    @abstractmethod
    def store(self, filepath: str | Path, content: BinaryIO) -> bool:
        """
        Store data in the storage.

        Parameters
        ----------
        filepath : str | Path
            The path where the data will be stored in the storage (including the filename).
        content : BinaryIO
            The data to be stored.

        Returns
        -------
        bool
            True if the data was stored successfully, False otherwise.
        """

    @abstractmethod
    def retrieve(self, filepath: str | Path) -> BinaryIO:
        """
        Retrieve data from the storage.

        Parameters
        ----------
        filepath : str | Path
            The path where the data is stored in the storage (including the filename).

        Returns
        -------
        BinaryIO
            The data retrieved from the storage.
        """

    @abstractmethod
    def url(self, filepath: str | Path) -> str:
        """
        Get the URL of the file.

        Parameters
        ----------
        filepath : str | Path
            The path where the file is stored in the storage (including the filename).

        Returns
        -------
        str
            The URL of the file.
        """


class StorageManagerInterface(ABC):
    """Interface for storage manager."""

    @abstractmethod
    def add_provider(self, name: str, provider: StorageProviderInterface) -> None:
        """
        Add a storage provider.

        Parameters
        ----------
        name : str
            The name of the storage provider.
        provider : StorageProviderInterface
            The storage provider to add.
        """

    @abstractmethod
    def remove_provider(self, name: str) -> None:
        """
        Remove a storage provider.

        Parameters
        ----------
        name : str
            The name of the storage provider.
        """

    @abstractmethod
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

    @property
    @abstractmethod
    def default(self) -> StorageProviderInterface:
        """
        Get the default storage provider based on the settings.

        Returns
        -------
        StorageProviderInterface
            The default storage provider.
        """
