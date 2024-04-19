import logging
from pathlib import Path
from typing import BinaryIO

from server.constants import PUBLIC_STORAGE_PATH
from server.webserver.interfaces import WebServerInterface

from .interfaces import StorageProviderInterface

_LOGGER = logging.getLogger(__name__)


class LocalStorage(StorageProviderInterface):
    """Implementation of the local storage provider."""

    def __init__(self, webserver: WebServerInterface) -> None:
        self._webserver = webserver

    def store(self, filepath: str | Path, content: BinaryIO) -> bool:
        """
        Store data in the local storage.

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
        try:
            with open(PUBLIC_STORAGE_PATH / filepath, "wb") as file:
                file.write(content.read())
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to store data in local storage: {e}")
            return False

    def retrieve(self, filepath: str | Path) -> BinaryIO:
        """
        Retrieve data from the local storage.

        Parameters
        ----------
        filepath : str | Path
            The path where the data is stored in the storage (including the filename).

        Returns
        -------
        BinaryIO
            The data retrieved from the storage.
        """
        return open(PUBLIC_STORAGE_PATH / filepath, "rb")

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
        route = self._webserver.http.get_route("public")
        addr = self._webserver.address
        path = route.canonical if route else ""

        return f"{addr}{path}/{filepath}"
