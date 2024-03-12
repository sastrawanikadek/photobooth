from server.utils.helpers.serialization import json_serialize
from server.utils.pydantic_fields import SlugStr
from server.utils.supports.collection import Collection

from .interfaces import _DT, SettingsManagerInterface
from .models import Setting, SettingInfo, SettingSchema
from .repositories import BackupSettingsRepository, SettingsRepository


class SettingsManager(SettingsManagerInterface):
    """
    Implementation of the settings manager.

    Attributes
    ----------
    _settings : dict[str, dict[str, SettingInfo]]
        A dictionary of settings, keyed by source and then by key.
    _schemas : dict[str, dict[str, SettingSchema]]
        A dictionary of setting schemas, keyed by source and then by key.
    """

    _settings: dict[str, dict[str, SettingInfo]] = {}
    _schemas: dict[str, dict[str, SettingSchema]] = {}

    def __init__(
        self, settings_repo: SettingsRepository, backup_repo: BackupSettingsRepository
    ) -> None:
        """Initialize the settings manager."""
        self._settings_repo = settings_repo
        self._backup_repo = backup_repo

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
                setting = settings.first(
                    lambda args: args[0].key == schema.key and args[0].source == source
                )
                setting_value = json_serialize(
                    (setting.value if setting is not None else schema.default_value)
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
                    id=item.id,
                    source=item.source,
                    value=(
                        item.parsed_value
                        if self._schemas[item.source][item.key].type != "string"
                        else item.value
                    ),
                    **self._schemas[item.source][item.key].model_dump(),
                )
            }
            for item in settings
        }

    async def add_schema(
        self, source: str, schema: SettingSchema, persist: bool = False
    ) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        persist : bool
            Whether to persist the schema to the database, by default False.
        """
        self._schemas.setdefault(source, {})[schema.key] = schema

        setting_id: int | None = None
        setting_value: object | None = None

        if persist:
            setting = await self._settings_repo.create(
                Setting(
                    source=source,
                    key=schema.key,
                    value=schema.default_value,
                )
            )
            setting_id = setting.id
            setting_value = (
                setting.parsed_value if schema.type != "string" else setting.value
            )

        self._settings.setdefault(source, {})[schema.key] = SettingInfo(
            id=setting_id,
            source=source,
            value=setting_value,
            **schema.model_dump(),
        )

    async def add_schemas(
        self,
        schemas: dict[SlugStr, list[SettingSchema]],
        *,
        persist: bool = False,
        schema_only: bool = False,
    ) -> None:
        """
        Add a new settings schema to the settings manager.

        Parameters
        ----------
        schemas : dict[SlugStr, list[SettingSchema]]
            The schemas of the settings to add, keyed by their source.
        persist : bool
            Whether to persist the schema to the database, by default False.
        schema_only : bool
            Whether to only add the schema to the settings manager, by default False.
        """
        settings: list[Setting] = []

        for source, source_schemas in schemas.items():
            for schema in source_schemas:
                self._schemas.setdefault(source, {})[schema.key] = schema
                settings.append(
                    Setting(
                        source=source,
                        key=schema.key,
                        value=schema.default_value,
                    )
                )

        if persist:
            settings_collection = await self._settings_repo.create_many(settings)
            settings = settings_collection.to_list()

        if not schema_only:
            for setting in settings:
                self._settings.setdefault(setting.source, {})[
                    setting.key
                ] = SettingInfo(
                    id=setting.id,
                    source=setting.source,
                    value=(
                        setting.parsed_value
                        if self._schemas[setting.source][setting.key].type != "string"
                        else setting.value
                    ),
                    **self._schemas[setting.source][setting.key].model_dump(),
                )

    def get_all(self) -> Collection[SettingInfo]:
        """
        Get all settings from different sources as a collection.

        Returns
        -------
        Collection[SettingInfo]
            A collection of settings from all sources.
        """
        settings: list[SettingInfo] = []

        for source_settings in self._settings.values():
            for setting in source_settings.values():
                settings.append(setting)

        return Collection(settings)

    def get_value(
        self, source: str, key: str, default: _DT | None = None
    ) -> object | _DT | None:
        """
        Get a setting value by its source and key.

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
            The setting value with the given source and key or the default value if it does not exist.
        """
        if source in self._settings and key in self._settings[source]:
            setting = self._settings[source][key]

            if setting.value is not None:
                return setting.value
            elif setting.default_value is not None:
                return setting.default_value

        return default

    def set_value(self, source: str, key: str, value: object) -> None:
        """
        Set a setting value by its source and key.

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

    def clear(self, source: str) -> None:
        """
        Clear all settings from the given source.

        Parameters
        ----------
        source : str
            The source of the settings to clear, it can only be a component slug.
        """
        if source == "system":
            raise ValueError("Cannot clear system settings")

        self._settings.pop(source, None)
