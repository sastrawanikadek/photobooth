from uuid import UUID

from server.database.interfaces import DatabaseInterface
from server.utils.helpers.serialization import json_deserialize, json_serialize
from server.utils.supports.collection import Collection

from .events import SettingUpdatedEvent
from .interfaces import DefaultType, SettingsManagerInterface
from .models import Setting, SettingInfo, SettingSchema
from .repositories import SettingsRepository
from .utils import generate_setting_uuid


class SettingsManager(SettingsManagerInterface):
    """
    Implementation of the settings manager.

    Attributes
    ----------
    _settings : dict[str, SettingInfo]
        A dictionary of settings, keyed by the UUID.
    _schemas : dict[str, dict[str, SettingSchema]]
        A dictionary of setting schemas, keyed by source and then by key.
    """

    _settings: dict[str, SettingInfo] = {}
    _schemas: dict[str, dict[str, SettingSchema]] = {}

    def __init__(
        self,
        settings_repo: SettingsRepository,
        db: DatabaseInterface,
    ) -> None:
        """Initialize the settings manager."""
        self._settings_repo = settings_repo
        self._db = db

    async def sync(self) -> None:
        """Sync the settings with the database."""
        settings = await self._settings_repo.get()

        new_settings: list[Setting] = []

        for source, source_settings in self._schemas.items():
            for schema in source_settings.values():
                uuid = generate_setting_uuid(source, schema.key)
                setting = settings.first(lambda args: args[0].uuid == uuid)

                if setting:
                    continue

                new_settings.append(
                    Setting(
                        uuid=uuid,
                        source=source,
                        key=schema.key,
                        value=json_serialize(schema.default_value),
                    )
                )

        settings += await self._settings_repo.create_many(new_settings)

        self._settings = {
            str(item.uuid): SettingInfo(
                uuid=item.uuid,
                source=item.source,
                value=(
                    item.parsed_value
                    if self._schemas[item.source][item.key].type != "string"
                    else item.value
                ),
                **self._schemas[item.source][item.key].model_dump(),
            )
            for item in settings
            if item.source in self._schemas and item.key in self._schemas[item.source]
        }

    async def add_setting(
        self,
        source: str,
        schema: SettingSchema,
        value: object | None = None,
        persist: bool = True,
    ) -> None:
        """
        Add a new setting to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        value : object | None
            The value of the setting, by default None.
        persist : bool
            Whether to persist the setting to the database, by default True.
        """
        self._schemas.setdefault(source, {})[schema.key] = schema

        setting_uuid = generate_setting_uuid(source, schema.key)
        setting_value: object | None = value or schema.default_value

        if persist:
            await self._settings_repo.create(
                Setting(
                    uuid=setting_uuid,
                    source=source,
                    key=schema.key,
                    value=json_serialize(setting_value),
                )
            )

        self._settings[str(setting_uuid)] = SettingInfo(
            uuid=setting_uuid,
            source=source,
            value=setting_value,
            **schema.model_dump(),
        )

    async def add_settings(
        self,
        source: str,
        schemas: list[SettingSchema],
        values: dict[str, object | None] = {},
        persist: bool = True,
    ) -> None:
        """
        Add a new settings to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schemas : list[SettingSchema]
            The schemas of the settings.
        values : dict[str, object | None]
            The values of the settings, keyed by their key.
        persist : bool
            Whether to persist the settings to the database, by default True.
        """
        new_settings: list[Setting] = []

        for schema in schemas:
            self._schemas.setdefault(source, {})[schema.key] = schema

            setting_uuid = generate_setting_uuid(source, schema.key)
            setting_value: object | None = (
                values.get(schema.key) or schema.default_value
            )

            self._settings[str(setting_uuid)] = SettingInfo(
                uuid=setting_uuid,
                source=source,
                value=setting_value,
                **schema.model_dump(),
            )

            new_settings.append(
                Setting(
                    uuid=setting_uuid,
                    source=source,
                    key=schema.key,
                    value=json_serialize(setting_value),
                )
            )

        if persist:
            await self._settings_repo.create_many(new_settings)

    async def add_schema(
        self, source: str, schema: SettingSchema, sync: bool = True
    ) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schema : SettingSchema
            The schema of the setting.
        sync : bool
            Whether to sync the settings with the database, by default True.
        """
        self._schemas.setdefault(source, {})[schema.key] = schema

        if sync:
            await self.sync()

    async def add_schemas(
        self,
        source: str,
        schemas: list[SettingSchema],
        sync: bool = True,
    ) -> None:
        """
        Add a new settings schema to the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        schemas : list[SettingSchema]
            The schemas of the settings.
        sync : bool
            Whether to sync the settings with the database, by default True.
        """
        for schema in schemas:
            self._schemas.setdefault(source, {})[schema.key] = schema

        if sync:
            await self.sync()

    def remove_schema(self, source: str, key: str) -> None:
        """
        Remove a setting schema from the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        key : str
            The key of the setting.
        """
        if source not in self._schemas or key not in self._schemas[source]:
            return

        uuid = generate_setting_uuid(source, key)
        self._settings.pop(str(uuid), None)
        self._schemas[source].pop(key)

    def remove_schemas(self, source: str, keys: list[str]) -> None:
        """
        Remove setting schemas from the settings manager.

        Parameters
        ----------
        source : str
            The source of the setting, it can be "system" or component slug.
        keys : list[str]
            The keys of the settings.
        """
        for key in keys:
            if source not in self._schemas or key not in self._schemas[source]:
                continue

            uuid = generate_setting_uuid(source, key)
            self._settings.pop(str(uuid), None)
            self._schemas[source].pop(key)

    def get_all(self) -> Collection[SettingInfo]:
        """
        Get all settings from different sources as a collection.

        Returns
        -------
        Collection[SettingInfo]
            A collection of settings from all sources.
        """
        return Collection(self._settings.values())

    def get_value(
        self,
        *,
        uuid: str | UUID | None = None,
        source: str | None = None,
        key: str | None = None,
        default: DefaultType | None = None,
    ) -> object | DefaultType | None:
        """
        Get a setting value by its UUID or source and key.

        Parameters
        ----------
        uuid : str | UUID | None
            The UUID of the setting.
        source : str | None
            The source of the setting.
        key : str | None
            The key of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given UUID or source and key or the default value if it does not exist.
        """
        uuid_str = str(uuid) if uuid else ""

        if source and key:
            uuid_str = str(generate_setting_uuid(source, key))

        if uuid_str not in self._settings:
            return default

        setting = self._settings[uuid_str]

        return setting.value or setting.default_value

    async def set_value(
        self, uuid: str | UUID, value: object, persist: bool = True
    ) -> None:
        """
        Set a setting value by its UUID.

        Parameters
        ----------
        uuid : str | UUID
            The UUID of the setting.
        value : object
            The value of the setting.
        persist : bool
            Whether to persist the setting update to the database, by default True.
        """
        uuid_str = str(uuid)

        if uuid_str not in self._settings:
            return

        local_setting = self._settings[uuid_str]
        parsed_value = (
            json_deserialize(value) if local_setting.type != "string" else value
        )

        local_setting.value = parsed_value

        if persist:
            setting = await self._settings_repo.find_by_uuid(uuid_str)

            if setting:
                setting.value = json_serialize(parsed_value)
                await self._settings_repo.update(setting)
            else:
                await self._settings_repo.create(
                    Setting(
                        uuid=uuid_str,
                        source=local_setting.source,
                        key=local_setting.key,
                        value=json_serialize(value),
                    )
                )

        SettingUpdatedEvent(local_setting).dispatch()

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
