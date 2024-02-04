from abc import ABC, abstractmethod

from pendulum import DateTime
from typing_extensions import Self


class CameraManagerInterface(ABC):
    """
    Interface for camera manager.

    Camera manager is responsible for detecting and connecting to a camera device.

    Attributes
    ----------
    camera : CameraDeviceInterface | None
        The connected camera device.
    """

    camera: "CameraDeviceInterface" | None = None

    @staticmethod
    @abstractmethod
    def auto_detect() -> list[tuple[str, str]]:
        """
        Detect all cameras connected to the computer.

        Returns
        -------
        list[tuple[str, str]]
            A list of tuples containing the camera model and address.
        """

    @abstractmethod
    def connect(self, address: str | None = None) -> Self:
        """
        Connect to a first camera or a camera with a specific address.

        Parameters
        ----------
        address : str | None
            The address of the camera to connect to.

        Returns
        -------
        Self
            The camera manager.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the camera."""


class CameraDeviceInterface(ABC):
    """
    Interface for camera device.

    Attributes
    ----------
    last_active : pendulum.DateTime
        The last time the camera was active.
    """

    last_active: DateTime

    @abstractmethod
    async def capture(self) -> bytes:
        """
        Capture an image and store it in memory.

        Returns
        -------
        bytes
            The image data.
        """

    @abstractmethod
    async def capture_preview(self) -> bytes:
        """
        Capture an preview image.

        Returns
        -------
        bytes
            The image data.
        """

    @abstractmethod
    async def capture_and_download(self, filename: str) -> bytes:
        """
        Capture an image, download it to the computer and remove it from the camera.

        Parameters
        ----------
        filename : str
            The filename to store the image in.

        Returns
        -------
        bytes
            The image data.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Close the connection to the camera.
        """
