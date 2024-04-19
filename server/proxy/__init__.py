"""Module for the proxy to the application instance."""

from ..interfaces import PhotoboothInterface
from .interfaces import PhotoboothAppInterface


class PhotoboothApp(PhotoboothAppInterface):
    """The photobooth app."""

    def __init__(self, photobooth: PhotoboothInterface) -> None:
        self._photobooth = photobooth
        self.dispatch = photobooth.eventbus.dispatch  # type: ignore[assignment]
        self.listen = photobooth.eventbus.add_listener  # type: ignore[assignment]
        self.remove_listener = photobooth.eventbus.remove_listener  # type: ignore[assignment]
        self.bind = photobooth.dependency_container.bind  # type: ignore[assignment]
        self.singleton = photobooth.dependency_container.singleton  # type: ignore[assignment]
        self.inject_constructor = photobooth.dependency_injector.inject_constructor  # type: ignore[assignment]
        self.call_with_injection = photobooth.dependency_injector.call_with_injection  # type: ignore[assignment]
        self.get_component = photobooth.component_manager.get  # type: ignore[assignment]
        self.get_component_data = photobooth.component_manager.get_data  # type: ignore[assignment]
        self.add_setting_schema = photobooth.settings_manager.add_schema  # type: ignore[assignment]
        self.add_setting_schemas = photobooth.settings_manager.add_schemas  # type: ignore[assignment]
        self.remove_setting_schema = photobooth.settings_manager.remove_schema  # type: ignore[assignment]
        self.remove_setting_schemas = photobooth.settings_manager.remove_schemas  # type: ignore[assignment]
        self.get_setting_value = photobooth.settings_manager.get_value  # type: ignore[assignment]
        self.broadcast = photobooth.webserver.websocket.broadcast  # type: ignore[assignment]


_photobooth: PhotoboothAppInterface | None = None


def set_photobooth(photobooth: PhotoboothAppInterface) -> None:
    """Set the photobooth."""
    global _photobooth
    _photobooth = photobooth


def app() -> PhotoboothAppInterface:
    """Get the photobooth app instance."""
    if _photobooth is None:
        raise RuntimeError("Photobooth not set")

    return _photobooth
