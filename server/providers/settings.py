from .interface import ServiceProviderInterface


class SettingsServiceProvider(ServiceProviderInterface):
    """The settings service provider."""

    setting_schemas = {}
