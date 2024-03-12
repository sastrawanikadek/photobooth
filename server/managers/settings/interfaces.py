from abc import ABC, abstractmethod
from typing import TypeVar

from server.utils.pydantic_fields import SlugStr
from server.utils.supports.collection import Collection

from .models import SettingInfo, SettingSchema

_DT = TypeVar("_DT", bound=object)


class SettingsManagerInterface(ABC):
    """Interface for settings manager implementations."""

    @abstractmethod
    async def sync(self) -> None:
        """Sync the settings with the database."""

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def get_all(self) -> Collection[SettingInfo]:
        """
        Get all settings from different sources as a collection.

        Returns
        -------
        Collection[SettingInfo]
            A collection of settings from all sources.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def clear(self, source: str) -> None:
        """
        Clear all settings from the given source.

        Parameters
        ----------
        source : str
            The source of the settings to clear, it can only be a component slug.
        """
