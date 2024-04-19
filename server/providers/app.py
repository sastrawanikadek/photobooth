from server.managers.settings.repositories import SettingsRepository

from .base import ServiceProvider


class AppServiceProvider(ServiceProvider):
    """The application service provider."""

    singletons = {
        SettingsRepository: SettingsRepository,
    }
