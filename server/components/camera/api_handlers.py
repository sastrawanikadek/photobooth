import asyncio
import base64
import functools
from typing import Callable, Coroutine, TypeVar
from uuid import uuid4

import pendulum
from aiohttp import web
from typing_extensions import Self

from server.eventbus.interfaces import EventBusInterface
from server.utils.helpers.function import safe_invoke
from server.utils.supports.http_response import HTTPResponse

from .dtos import CameraCaptureResponseDTO
from .events import CameraActiveEvent
from .exceptions import CameraError
from .interfaces import CameraDeviceInterface, CameraManagerInterface

_DecoratedReturn = TypeVar("_DecoratedReturn")


class APIHandler:
    """Handler for API requests related to camera component."""

    _camera: CameraDeviceInterface

    def __init__(
        self, camera_manager: CameraManagerInterface, eventbus: EventBusInterface
    ) -> None:
        self._camera_manager = camera_manager
        self._eventbus = eventbus

    def _camera_status_aware(  # type: ignore
        func: Callable[..., Coroutine[None, None, _DecoratedReturn]]
    ) -> Callable[..., Coroutine[None, None, _DecoratedReturn]]:
        """Decorator to ensure that the camera is connected before invoking the handler."""

        @functools.wraps(func)
        async def wrapper(
            self: Self, *args: object, **kwargs: object
        ) -> _DecoratedReturn:
            retry = 0
            max_retry = 5

            if self._camera_manager.camera is None:
                self._eventbus.dispatch(CameraActiveEvent())

            while self._camera_manager.camera is None:
                if retry >= max_retry:
                    raise CameraError("Camera is not connected")

                await asyncio.sleep(1)
                retry += 1

            self._camera = self._camera_manager.camera

            return await safe_invoke(func, self, *args, **kwargs)

        return wrapper

    @_camera_status_aware
    async def capture(self) -> web.StreamResponse:
        filename = str(uuid4()) + ".jpg"
        image_bytes = await self._camera.capture_and_download(filename)
        self._last_active = pendulum.now()
        base64_bytes = base64.b64encode(image_bytes)

        return HTTPResponse.json(
            data=CameraCaptureResponseDTO(image=base64_bytes.decode())
        )
