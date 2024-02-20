import asyncio
import logging
from typing import cast

import pendulum

from server.eventbus import EventBusInterface
from server.injector import DependencyContainerInterface
from server.managers.component import ComponentInterface
from server.managers.settings import (
    Display,
    SettingSchema,
    SettingsManagerInterface,
    ValueType,
)

from .constants import SETTING_IDLE_TIMEOUT_DURATION, SLUG
from .events import CameraActiveEvent, CameraConnectedEvent, CameraDisconnectedEvent
from .interfaces import CameraManagerInterface
from .services import CameraManager
from .widgets import RadioWidget, ToggleWidget

_LOGGER = logging.getLogger(__name__)


class Camera(ComponentInterface):
    _is_idle = False

    def __init__(
        self,
        container: DependencyContainerInterface,
        eventbus: EventBusInterface,
        settings_manager: SettingsManagerInterface,
    ) -> None:
        self._camera_manager = CameraManager()
        self._eventbus = eventbus
        self._settings_manager = settings_manager

        # Register the camera manager as a dependency
        container.singleton(CameraManagerInterface, self._camera_manager)

        # Register event listeners
        self._eventbus.add_listener(CameraActiveEvent, self._on_camera_active)

        asyncio.create_task(self._check_connectivity())
        asyncio.create_task(self._check_inactivity())

    def _on_camera_active(self, _: CameraActiveEvent) -> None:
        """
        Event handler for when the camera is active.

        It sets the camera as not idle.
        """
        self._is_idle = False

    async def _on_camera_connected(self) -> None:
        """
        Handler for when the camera is connected.

        It update the settings.
        """
        await self._update_camera_settings()

        self._eventbus.dispatch(CameraConnectedEvent())
        _LOGGER.info("Camera connected")

    async def _on_camera_idle(self) -> None:
        """
        Handler for when the camera is idle.

        It disconnects the camera, clear the settings and dispatches the CameraDisconnectedEvent.
        """
        self._is_idle = True
        await self._camera_manager.disconnect()

        self._settings_manager.clear(SLUG)

        self._eventbus.dispatch(CameraDisconnectedEvent())
        _LOGGER.info("Camera disconnected due to inactivity")

    async def _check_connectivity(self) -> None:
        while True:
            if self._is_idle:
                await asyncio.sleep(1)
                continue

            if self._camera_manager.camera is None:
                if self._camera_manager.connect().camera is not None:
                    await self._on_camera_connected()

            await asyncio.sleep(5)

    async def _check_inactivity(self) -> None:
        while True:
            now = pendulum.now()
            camera = self._camera_manager.camera

            if camera is not None:
                idleTimeoutDuration = self._settings_manager.get_value(
                    SLUG, SETTING_IDLE_TIMEOUT_DURATION, 300
                )

                if camera.last_active.diff(now).in_seconds() >= idleTimeoutDuration:
                    await self._on_camera_idle()

            await asyncio.sleep(60)

    async def _update_camera_settings(self) -> None:
        """Updates the camera settings."""
        if self._camera_manager.camera is None:
            return

        config_widgets = await self._camera_manager.camera.get_config()
        setting_schemas: dict[str, list[SettingSchema]] = {SLUG: []}

        for widget in config_widgets:
            setting_display = (
                "select"
                if isinstance(widget, RadioWidget) and len(widget.options) > 3
                else widget.type
            )
            setting_type = "integer" if isinstance(widget, ToggleWidget) else "string"
            setting_options = (
                widget.options if isinstance(widget, RadioWidget) else None
            )
            setting_schemas[SLUG].append(
                SettingSchema(
                    key=widget.name,
                    title=widget.label,
                    display=cast(Display, setting_display),
                    type=cast(ValueType, setting_type),
                    default_value=widget.value,
                    options=setting_options,
                )
            )

        await self._settings_manager.add_schemas(setting_schemas)
