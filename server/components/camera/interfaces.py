from abc import ABC, abstractmethod

from pendulum import DateTime

from server.utils.supports.collection import Collection

from .widgets import CameraWidget


class CameraDeviceInterface(ABC):
    """
    Interface for camera device.

    Attributes
    ----------
    last_active : pendulum.DateTime
        The last time the camera was active.
    """

    last_active: DateTime

    @property
    @abstractmethod
    def model(self) -> str:
        """The model of the camera."""

    @property
    @abstractmethod
    def canonical_name(self) -> str:
        """The canonical name of the camera model."""

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
    async def get_config(self) -> list[CameraWidget]:
        """Get the configuration provided by the camera."""

    @abstractmethod
    async def set_single_config(self, name: str, value: object) -> None:
        """
        Set a single configuration value on the camera.

        Parameters
        ----------
        name : str
            The name of the configuration.
        value : object
            The value to set.
        """

    @abstractmethod
    async def set_configs(self, configs: dict[str, object]) -> None:
        """
        Set multiple configuration values on the camera.

        Parameters
        ----------
        configs : dict[str, object]
            The configuration values to set.
        """

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the camera."""

    @abstractmethod
    async def ping(self) -> bool:
        """Check if the camera is still connected."""


class CameraManagerInterface(ABC):
    """
    Interface for camera manager.

    Camera manager is responsible for detecting and connecting to a camera device.

    Attributes
    ----------
    camera : CameraDeviceInterface | None
        The connected camera device.
    """

    camera: CameraDeviceInterface | None = None

    @staticmethod
    @abstractmethod
    def auto_detect() -> Collection[tuple[str, str]]:
        """
        Detect all cameras connected to the computer.

        Returns
        -------
        Collection[tuple[str, str]]
            A collection of tuples containing the camera model and address.
        """

    @abstractmethod
    def connect(self, address: str | None = None) -> CameraDeviceInterface | None:
        """
        Connect to a first camera or a camera with a specific address.

        Parameters
        ----------
        address : str | None
            The address of the camera to connect to.

        Returns
        -------
        CameraDeviceInterface | None
            The connected camera device or None if no camera is found.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the camera."""
