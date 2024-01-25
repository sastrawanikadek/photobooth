from abc import ABC, abstractmethod
from typing import TypeVar

from .models import SettingInfo, SettingSchema

_DT = TypeVar("_DT", bound=object)


class SettingsManagerInterface(ABC):
    """Interface for settings manager implementations."""

    @abstractmethod
    async def load(self, schemas: dict[str, list[SettingSchema]]) -> None:
        """
        Load the settings from the given schemas.

        Parameters
        ----------
        schemas : dict[str, list[SettingSchema]]
            A dictionary of setting schemas, keyed by source.
        """

    @abstractmethod
    async def sync(self) -> None:
        """Sync the settings with the database."""

    @abstractmethod
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

    @abstractmethod
    def get_all(self) -> list[SettingInfo]:
        """
        Get all settings from different sources as a list.

        Returns
        -------
        list[SettingInfo]
            A list of settings from all sources.
        """

    @abstractmethod
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

    @abstractmethod
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
