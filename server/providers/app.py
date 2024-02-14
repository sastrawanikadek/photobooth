from server.managers.settings import BackupSettingsRepository, SettingsRepository

from .interface import ServiceProviderInterface


class AppServiceProvider(ServiceProviderInterface):
    """The application service provider."""

    singletons = {
        BackupSettingsRepository: BackupSettingsRepository,
        SettingsRepository: SettingsRepository,
    }
