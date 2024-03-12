from aiohttp import web

from server.utils.supports.http_response import HTTPResponse

from ..interfaces import SettingsManagerInterface


class HTTPAPIHandler:
    """Handler for API requests related to settings."""

    def __init__(self, settings_manager: SettingsManagerInterface) -> None:
        self._settings_manager = settings_manager

    def get_all(self) -> web.StreamResponse:
        """Get all settings."""
        settings = self._settings_manager.get_all()

        return HTTPResponse.json(data=settings)
