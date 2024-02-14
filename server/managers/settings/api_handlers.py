from .interfaces import SettingsManagerInterface
from .models import SettingInfo


class APIHandler:
    """Handler for API requests related to settings."""

    def __init__(self, settings_manager: SettingsManagerInterface) -> None:
        self._settings_manager = settings_manager

    def get_all(self) -> list[SettingInfo]:
        """Get all settings."""
        return self._settings_manager.get_all()
