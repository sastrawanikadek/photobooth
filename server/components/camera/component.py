import asyncio
import logging
from typing import cast

import pendulum

from server.dependency_injection.interfaces import DependencyContainerInterface
from server.eventbus.interfaces import EventBusInterface
from server.events import AppReadyEvent
from server.managers.components.base import Component
from server.managers.settings.events import SettingUpdatedEvent
from server.managers.settings.models import Display, SettingSchema, ValueType
from server.webserver.interfaces import WebServerInterface

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


class Camera(Component):
    _is_idle = False
    _camera_config_schema_keys: list[str] = []

    def __init__(
        self,
        container: DependencyContainerInterface,
        eventbus: EventBusInterface,
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
        webserver : WebServerInterface
            The web server.
        """
        super().__init__(SLUG)

        self._camera_manager = CameraManager()
        self._eventbus = eventbus
        self._webserver = webserver

        # Register the camera manager as a dependency
        container.singleton(CameraManagerInterface, self._camera_manager)

        # Register event listeners
        self._eventbus.add_listener(AppReadyEvent, self._on_app_ready)
        self._eventbus.add_listener(CameraActiveEvent, self._on_camera_active)
        self._eventbus.add_listener(
            CameraDisconnectedEvent, self._on_camera_disconnected
        )
        self._eventbus.add_listener(SettingUpdatedEvent, self._on_setting_updated)

    def _on_app_ready(self, _: AppReadyEvent) -> None:
        """
        Event handler for when the app is ready.

        It tries to connect to the camera.
        """
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

        # Remove the camera settings
        self.remove_setting_schemas(self._camera_config_schema_keys)

        _LOGGER.info("Camera disconnected")

    async def _on_setting_updated(self, event: SettingUpdatedEvent) -> None:
        """
        Event handler for when a setting is updated.

        It sets the configuration on the camera.

        Parameters
        ----------
        event : SettingUpdatedEvent
            The event.
        """
        if not self._camera_manager.camera or not event.data.key.startswith(
            self._camera_manager.camera.canonical_name
        ):
            return

        await self._camera_manager.camera.set_single_config(
            event.data.key.removeprefix(
                f"{self._camera_manager.camera.canonical_name}_"
            ),
            event.data.value,
        )

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
        await self._apply_settings(camera)

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

            if not self._camera_manager.camera:
                if camera := self._camera_manager.connect():
                    await self._on_camera_connected(camera)
            else:
                if not await self._camera_manager.camera.ping():
                    CameraDisconnectedEvent().dispatch()

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
                idleTimeoutDuration = self.get_setting_value(
                    SETTING_IDLE_TIMEOUT_DURATION, 300
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
        setting_schemas: list[SettingSchema] = []

        for widget in config_widgets:
            setting_key = f"{camera.canonical_name}_{widget.name}"
            setting_display = (
                "select"
                if isinstance(widget, RadioWidget) and len(widget.options) > 3
                else widget.type
            )
            setting_type = "integer" if isinstance(widget, ToggleWidget) else "string"
            setting_options = (
                widget.options if isinstance(widget, RadioWidget) else None
            )

            setting_schemas.append(
                SettingSchema(
                    key=setting_key,
                    title=widget.label,
                    group="Camera",
                    display=cast(Display, setting_display),
                    type=cast(ValueType, setting_type),
                    default_value=widget.value,
                    options=setting_options,
                )
            )
            self._camera_config_schema_keys.append(setting_key)

        await self.add_setting_schemas(setting_schemas)

    async def _apply_settings(self, camera: CameraDeviceInterface) -> None:
        """
        Apply the settings to the camera.

        It sets the configuration on the camera.

        Parameters
        ----------
        camera : CameraDeviceInterface
            The camera device.
        """
        configs = {}

        for key in self._camera_config_schema_keys:
            value = self.get_setting_value(key)

            if value is None:
                continue

            configs[key.removeprefix(f"{camera.canonical_name}_")] = value

        await camera.set_configs(configs)

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
