from abc import ABC, abstractmethod
from typing import TypeVar, overload
from uuid import UUID

from server.utils.supports.collection import Collection

from .models import SettingInfo, SettingSchema

DefaultType = TypeVar("DefaultType", bound=object)


class SettingsManagerInterface(ABC):
    """Interface for settings manager implementations."""

    @abstractmethod
    async def sync(self) -> None:
        """Sync the settings with the database."""

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def get_all(self) -> Collection[SettingInfo]:
        """
        Get all settings from different sources as a collection.

        Returns
        -------
        Collection[SettingInfo]
            A collection of settings from all sources.
        """

    @overload
    @abstractmethod
    def get_value(
        self, *, uuid: str | UUID, default: DefaultType | None = None
    ) -> object | DefaultType | None:
        """
        Get a setting value by its UUID.

        Parameters
        ----------
        uuid : str | UUID
            The UUID of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given UUID or the default value if it does not exist.
        """

    @overload
    @abstractmethod
    def get_value(
        self, *, source: str, key: str, default: DefaultType | None = None
    ) -> object | DefaultType | None:
        """
        Get a setting value by its source and key.

        Parameters
        ----------
        source : str
            The source of the setting.
        key : str
            The key of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given source and key or the default value if it does not exist.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def clear(self, source: str) -> None:
        """
        Clear all settings from the given source.

        Parameters
        ----------
        source : str
            The source of the settings to clear, it can only be a component slug.
        """
