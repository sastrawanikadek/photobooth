from pathlib import Path
from typing import BinaryIO

from aiohttp import web
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from server.managers.storages.constants import LOCAL_STORAGE_PROVIDER
from server.managers.storages.interfaces import StorageManagerInterface
from server.utils.helpers.file import generate_filename, get_file_size


class File:
    """A file class that provides a set of methods to work with files."""

    def __init__(
        self, file: web.FileField, storage_manager: StorageManagerInterface
    ) -> None:
        """
        Initialize the file.

        Parameters
        ----------
        file : web.FileField
            The file uploaded in the request.
        """
        self._name: str = file.filename
        self._io: BinaryIO = file.file
        self._size = get_file_size(self._io)
        self._content_type: str = file.content_type
        self._storage_manager = storage_manager

    @property
    def size(self) -> int:
        """Get the size of the file."""
        return self._size

    @property
    def content_type(self) -> str:
        """Get the content type of the file."""
        return self._content_type

    @property
    def name(self) -> str:
        """Get the name of the file."""
        return self._name

    @property
    def extension(self) -> str:
        """Get the extension of the file."""
        return Path(self._name).suffix

    def save(
        self, path: str | Path | None = None, storage: str = LOCAL_STORAGE_PROVIDER
    ) -> str:
        """
        Save the file to the specified path.

        Parameters
        ----------
        path : str | Path | None
            The path to save the file to. If None, the file will be saved in the root directory.
        storage : str
            The storage provider to use. Default is the local storage.

        Returns
        -------
        str
            The URL of the file in the storage.
        """
        filename = generate_filename() + self.extension
        path = filename if path is None else f"{path}/{filename}"
        storage_provider = self._storage_manager.provider(storage)

        if storage_provider is None:
            raise ValueError(f'Storage provider "{storage}" not found')

        if not storage_provider.store(path, self._io):
            raise ValueError("Failed to store the file")

        return storage_provider.url(path)

    def __str__(self) -> str:
        """Return the string representation of the file."""
        return self.name

    def __repr__(self) -> str:
        """Return the string representation of the collection."""
        return "<File name={}, size={}, content_type={}>".format(
            self.name, self.size, self.content_type
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _: object, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.is_instance_schema(cls)
