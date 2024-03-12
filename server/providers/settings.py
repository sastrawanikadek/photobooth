from server.constants import SETTING_STORAGE_PROVIDER
from server.managers.settings import SettingOption, SettingSchema

from .base import ServiceProvider


class SettingsServiceProvider(ServiceProvider):
    """The settings service provider."""

    setting_schemas = {
        "system": [
            SettingSchema(
                key=SETTING_STORAGE_PROVIDER,
                title="Storage Provider",
                description="The storage provider for the application.",
                display="select",
                type="string",
                default_value="local",
                options=[
                    SettingOption(label="Local", value="local"),
                    SettingOption(label="Amazon S3", value="s3"),
                    SettingOption(label="Google Cloud Storage", value="gcs"),
                    SettingOption(label="Google Drive", value="drive"),
                ],
            )
        ]
    }
