from aiohttp import web

from server.utils.supports.http_response import HTTPResponse

from ..dtos import UpdateSettingRequestDTO
from ..interfaces import SettingsManagerInterface


class HTTPAPIHandler:
    """Handler for API requests related to settings."""

    def __init__(self, settings_manager: SettingsManagerInterface) -> None:
        self._settings_manager = settings_manager

    def get_all(self) -> web.StreamResponse:
        """Get all settings."""
        settings = self._settings_manager.get_all()

        return HTTPResponse.json(data=settings)

    async def update(
        self, uuid: str, request: UpdateSettingRequestDTO
    ) -> web.StreamResponse:
        """Update a setting."""
        if isinstance(request.value, str):
            value = request.value
        else:
            value = request.value.save()

        await self._settings_manager.set_value(uuid, value)

        return HTTPResponse.empty()
