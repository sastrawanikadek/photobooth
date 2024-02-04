import asyncio
import logging

import pendulum

from server.eventbus import EventBusInterface
from server.managers.component import ComponentInterface, ComponentManagerInterface

from .services import CameraManager

_LOGGER = logging.getLogger(__name__)


class Camera(ComponentInterface):
    _is_idle = False

    def __init__(
        self, component_manager: ComponentManagerInterface, eventbus: EventBusInterface
    ) -> None:
        self._component_manager = component_manager
        self._eventbus = eventbus
        self._camera_manager = CameraManager()

        asyncio.create_task(self._check_connectivity())
        asyncio.create_task(self._check_inactivity())

    async def _check_connectivity(self) -> None:
        while True:
            if self._is_idle:
                await asyncio.sleep(1)
                continue

            if self._camera_manager.camera is None:
                if self._camera_manager.connect().camera is not None:
                    _LOGGER.info("Camera connected")

            await asyncio.sleep(5)

    async def _check_inactivity(self) -> None:
        while True:
            now = pendulum.now()
            camera = self._camera_manager.camera

            if camera is not None:
                idleTimeoutDuration = 300  # 5 minutes

                if camera.last_active.diff(now).in_seconds() >= idleTimeoutDuration:
                    self._is_idle = True
                    await self._camera_manager.disconnect()
                    _LOGGER.info("Camera disconnected due to inactivity")

            await asyncio.sleep(60)
