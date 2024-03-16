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
from server.webserver import WebServerInterface

from .constants import (
    CHANNEL_CAMERA_CAPTURE_PREVIEW,
    SETTING_IDLE_TIMEOUT_DURATION,
    SLUG,
)
from .events import CameraActiveEvent, CameraConnectedEvent, CameraDisconnectedEvent
from .exceptions import CameraError
from .interfaces import CameraDeviceInterface, CameraManagerInterface
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
        webserver: WebServerInterface,
    ) -> None:
        """
        Initializes the camera component.

        Parameters
        ----------
        container : DependencyContainerInterface
            The dependency container.
        eventbus : EventBusInterface
            The event bus.
        settings_manager : SettingsManagerInterface
            The settings manager.
        webserver : WebServerInterface
            The web server.
        """
        self._camera_manager = CameraManager()
        self._eventbus = eventbus
        self._settings_manager = settings_manager
        self._webserver = webserver

        # Register the camera manager as a dependency
        container.singleton(CameraManagerInterface, self._camera_manager)

        # Register event listeners
        self._eventbus.add_listener(CameraActiveEvent, self._on_camera_active)
        self._eventbus.add_listener(
            CameraDisconnectedEvent, self._on_camera_disconnected
        )

        asyncio.create_task(self._check_connectivity())
        asyncio.create_task(self._check_inactivity())

    def _on_camera_active(self, _: CameraActiveEvent) -> None:
        """
        Event handler for when the camera is active.

        It sets the camera as not idle.
        """
        self._is_idle = False

    def _on_camera_disconnected(self, _: CameraDisconnectedEvent) -> None:
        """
        Event Handler for when the camera is disconnected.

        It reset the state of the camera and clear the settings.
        """
        self._camera_manager.camera = None
        self._is_idle = False

        self._settings_manager.clear(SLUG)
        _LOGGER.info("Camera disconnected")

    async def _on_camera_connected(self, camera: CameraDeviceInterface) -> None:
        """
        Handler for when the camera is connected.

        It update the settings.

        Parameters
        ----------
        camera : CameraDeviceInterface
            The camera device.
        """
        await self._update_camera_settings(camera)

        CameraConnectedEvent(camera).dispatch()

        asyncio.create_task(self._capture_preview(camera))
        _LOGGER.info("Camera connected")

    async def _on_camera_idle(self) -> None:
        """
        Handler for when the camera is idle.

        It disconnects the camera,
        clear the settings and dispatches the CameraDisconnectedEvent.
        """
        self._is_idle = True
        await self._camera_manager.disconnect()

        self._settings_manager.clear(SLUG)

        CameraDisconnectedEvent().dispatch()
        _LOGGER.info("Camera disconnected due to inactivity")

    async def _check_connectivity(self) -> None:
        """
        Check the camera connectivity.

        If the camera is not connected, it will try to connect.
        """
        while True:
            if self._is_idle:
                await asyncio.sleep(1)
                continue

            if self._camera_manager.camera is None:
                camera = self._camera_manager.connect().camera

                if camera is not None:
                    await self._on_camera_connected(camera)

            await asyncio.sleep(5)

    async def _check_inactivity(self) -> None:
        """
        Check the camera inactivity.

        If the camera is idle for a certain duration, it will be disconnected.
        """
        while True:
            now = pendulum.now()
            camera = self._camera_manager.camera

            if camera is not None:
                idleTimeoutDuration = self._settings_manager.get_value(
                    SLUG, SETTING_IDLE_TIMEOUT_DURATION, 300
                )

                if camera.last_active.diff(now).in_seconds() >= idleTimeoutDuration:
                    await self._on_camera_idle()

            await asyncio.sleep(30)

    async def _update_camera_settings(self, camera: CameraDeviceInterface) -> None:
        """
        Updates the camera settings.

        It gets the camera configuration and adds the settings to the settings manager.

        Parameters
        ----------
        camera : CameraDeviceInterface
            The camera device.
        """
        config_widgets = await camera.get_config()
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

    async def _capture_preview(self, camera: CameraDeviceInterface) -> None:
        """
        Capture a preview from the camera.

        Parameters
        ----------
        camera : CameraDeviceInterface
            The camera device.
        """
        while True:
            if not self._webserver.websocket.has_subscribers(
                CHANNEL_CAMERA_CAPTURE_PREVIEW
            ):
                await asyncio.sleep(1)
                continue

            if self._is_idle:
                CameraActiveEvent().dispatch()
                await asyncio.sleep(1)
                continue

            try:
                preview_bytes = await camera.capture_preview()
            except CameraError:
                break
            else:
                self._webserver.websocket.broadcast(
                    CHANNEL_CAMERA_CAPTURE_PREVIEW, preview_bytes.decode()
                )
