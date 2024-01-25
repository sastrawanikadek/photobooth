from typing import cast

from .interfaces import _DT, SettingsManagerInterface
from .models import Setting, SettingInfo, SettingSchema
from .repositories import BackupSettingsRepository, SettingsRepository


class SettingsManager(SettingsManagerInterface):
    _settings: dict[str, dict[str, SettingInfo]] = {}
    _schemas: dict[str, dict[str, SettingSchema]] = {}

    def __init__(
        self, settings_repo: SettingsRepository, backup_repo: BackupSettingsRepository
    ) -> None:
        """Initialize the settings manager."""
        self._settings_repo = settings_repo
        self._backup_repo = backup_repo

    async def load(self, schemas: dict[str, list[SettingSchema]]) -> None:
        """
        Load the settings from the given schemas.

        Parameters
        ----------
        schemas : dict[str, list[SettingSchema]]
            A dictionary of setting schemas, keyed by source.
        """
        self._schemas = {
            source: {schema.key: schema for schema in items}
            for source, items in schemas.items()
        }
        await self.sync()

    async def sync(self) -> None:
        """Sync the settings with the database."""
        settings = await self._settings_repo.get()

        if settings:
            await self._backup_repo.backup(settings)
        else:
            settings = await self._backup_repo.restore()

        new_settings = []

        for source, source_settings in self._schemas.items():
            for schema in source_settings.values():
                setting_value = next(
                    (
                        setting.value
                        for setting in settings
                        if setting.source == source and setting.key == schema.key
                    ),
                    schema.default_value,
                )

                new_settings.append(
                    Setting(
                        source=source,
                        key=schema.key,
                        value=setting_value,
                    )
                )

        settings = await self._settings_repo.overwrite(new_settings)
        self._settings = {
            item.source: {
                item.key: SettingInfo(
                    id=cast(int, item.id),
                    source=item.source,
                    value=item.value,
                    **self._schemas[item.source][item.key].model_dump(),
                )
            }
            for item in settings
        }

    def add_schema(self, source: str, schema: SettingSchema) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        """
        self._schemas.setdefault(source, {})[schema.key] = schema

    def get_all(self) -> list[SettingInfo]:
        """
        Get all settings from different sources as a list.

        Returns
        -------
        list[SettingInfo]
            A list of settings from all sources.
        """
        settings: list[SettingInfo] = []

        for source_settings in self._settings.values():
            for setting in source_settings.values():
                settings.append(setting)

        return settings

    def get(
        self, source: str, key: str, default: _DT | None = None
    ) -> object | _DT | None:
        """
        Get a setting by its source and key.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        key : str
            The key of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting with the given source and key or the default value if it does not exist.
        """
        if source in self._settings and key in self._settings[source]:
            setting = self._settings[source][key]

            if setting.value is not None:
                return setting.value
            elif setting.default_value is not None:
                return setting.default_value

        return default

    def set(self, source: str, key: str, value: object) -> None:
        """
        Set a setting by its source and key.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        key : str
            The key of the setting.
        value : object
            The value of the setting.
        """
        if source in self._settings and key in self._settings[source]:
            self._settings[source][key].value = value
