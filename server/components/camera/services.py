import asyncio
import functools
import logging
from typing import Callable, Coroutine, ParamSpec, TypeVar

import gphoto2 as gp
import pendulum
from typing_extensions import Self

from .exceptions import DeviceUSBNotFoundError, ModelNotFoundError
from .interfaces import CameraDeviceInterface, CameraManagerInterface

_LOGGER = logging.getLogger(__name__)
_P = ParamSpec("_P")
_DecoratedReturn = TypeVar("_DecoratedReturn")


class CameraManager(CameraManagerInterface):
    """
    Camera manager is responsible for detecting and connecting to a camera device.

    Attributes
    ----------
    camera : CameraDeviceInterface | None
        The connected camera device.
    """

    camera: CameraDeviceInterface | None = None

    @staticmethod
    def auto_detect() -> list[tuple[str, str]]:
        """
        Detect all cameras connected to the computer.

        Returns
        -------
        list[tuple[str, str]]
            A list of tuples containing the camera model and address.
        """
        return list(gp.Camera.autodetect())

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
        detected_cameras = self.auto_detect()

        if len(detected_cameras) == 0:
            _LOGGER.debug("No cameras detected")
            return self

        camera_info = next(
            (
                item
                for item in detected_cameras
                if address is None or (address is not None and item[1] == address)
            ),
            None,
        )

        if camera_info is None:
            return self

        name, addr = camera_info
        _LOGGER.debug("Connecting to camera %s at %s", name, addr)

        gp_camera = gp.Camera()
        gp_context = gp.Context()

        # Get the port informations and set it to the camera
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        idx = port_info_list.lookup_path(addr)
        gp_camera.set_port_info(port_info_list[idx])

        # Load all the camera abilities and set it to the camera
        abilities_list = gp.CameraAbilitiesList()
        abilities_list.load()
        idx = abilities_list.lookup_model(name)
        gp_camera.set_abilities(abilities_list[idx])

        # Initialize connection to the camera
        gp_camera.init(gp_context)

        self.camera = CameraDevice(gp_camera, gp_context)
        return self

    async def disconnect(self) -> None:
        """Disconnect the camera."""
        if self.camera is not None:
            await self.camera.close()
            self.camera = None


class CameraDevice(CameraDeviceInterface):
    """
    Integration to a camera device using gphoto2.

    Attributes
    ----------
    last_active : pendulum.DateTime
        The last time the camera was used.
    _camera : gp.Camera
        Object instance of the gphoto2 camera.
    _context : gp.Context
        Object instance of the gphoto2 context.
    _lock : asyncio.Lock
        Lock for synchronizing access to the camera.
    """

    last_active = pendulum.now()
    _lock = asyncio.Lock()

    def __init__(self, camera: gp.Camera, context: gp.Context):
        self._camera = camera
        self._context = context

    def _camera_activity(  # type: ignore
        func: Callable[..., Coroutine[None, None, _DecoratedReturn]]
    ) -> Callable[..., Coroutine[None, None, _DecoratedReturn]]:
        """Decorator to update the last active time when a camera activity is performed."""

        @functools.wraps(func)
        async def wrapper(
            self: Self, *args: object, **kwargs: object
        ) -> _DecoratedReturn:
            self.last_active = pendulum.now()
            return await func(*args, **kwargs)

        return wrapper

    @_camera_activity
    async def capture(self) -> bytes:
        """
        Capture an image and store it in memory.

        Returns
        -------
        bytes
            The image data.
        """
        async with self._lock:
            try:
                file_path = await asyncio.to_thread(
                    self._camera.capture(gp.GP_CAPTURE_IMAGE, self._context)
                )
                file = await asyncio.to_thread(
                    self._camera.file_get(
                        file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL
                    )
                )
            except gp.GPhoto2Error as e:
                self._error_handler(e)

        return bytes(file.get_data_and_size())

    @_camera_activity
    async def capture_preview(self) -> bytes:
        """
        Capture an preview image.

        Returns
        -------
        bytes
            The image data.
        """
        async with self._lock:
            try:
                file = gp.CameraFile()
                await asyncio.to_thread(
                    self._camera.capture_preview, file, self._context
                )
            except gp.GPhoto2Error as e:
                self._error_handler(e)

        return bytes(file.get_data_and_size())

    @_camera_activity
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
        async with self._lock:
            try:
                file_path = await asyncio.to_thread(
                    self._camera.capture, gp.GP_CAPTURE_IMAGE, self._context
                )
                file = await asyncio.to_thread(
                    self._camera.file_get,
                    file_path.folder,
                    file_path.name,
                    gp.GP_FILE_TYPE_NORMAL,
                )
                await asyncio.to_thread(
                    self._camera.file_delete, file_path.folder, file_path.name
                )
            except gp.GPhoto2Error as e:
                self._error_handler(e)

        await asyncio.to_thread(file.save, filename)
        return bytes(file.get_data_and_size())

    async def close(self) -> None:
        """Close the connection to the camera."""
        async with self._lock:
            try:
                await asyncio.to_thread(self._camera.exit, self._context)
            except gp.GPhoto2Error as e:
                self._error_handler(e)

    def _error_handler(self, exception: gp.GPhoto2Error) -> None:
        """Handle errors from the camera."""
        if exception.code == gp.GP_ERROR_MODEL_NOT_FOUND:
            raise ModelNotFoundError("The specified camera model was not found.")
        elif exception.code == gp.GP_ERROR_IO_USB_FIND:
            raise DeviceUSBNotFoundError("The camera is not connected to USB port.")
        else:
            raise exception
