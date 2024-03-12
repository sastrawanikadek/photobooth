from server.managers.settings import BackupSettingsRepository, SettingsRepository

from .base import ServiceProvider


class AppServiceProvider(ServiceProvider):
    """The application service provider."""

    singletons = {
        BackupSettingsRepository: BackupSettingsRepository,
        SettingsRepository: SettingsRepository,
    }
