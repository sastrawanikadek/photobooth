from server.managers.settings import (
    BackupSettingsRepository,
    SettingsRepository,
)

from .interfaces import ServiceProviderInterface


class AppServiceProvider(ServiceProviderInterface):
    """The application service provider."""

    singletons = {
        BackupSettingsRepository: BackupSettingsRepository,
        SettingsRepository: SettingsRepository,
    }


class SettingsServiceProvider(ServiceProviderInterface):
    """The settings service provider."""

    setting_schemas = {}
