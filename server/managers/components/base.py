from server.managers.settings.interfaces import DefaultType
from server.managers.settings.models import SettingSchema
from server.proxy import app
from server.utils.pydantic_fields.string import SlugStr


class Component:
    """
    Base class for all components.

    Attributes
    ----------
    slug : SlugStr
        Unique identifier for the component.
    """

    def __init__(self, slug: SlugStr) -> None:
        self.slug = slug

    async def add_setting_schema(
        self, schema: SettingSchema, sync: bool = True
    ) -> None:
        """
        Add a new setting schema to the settings manager.

        Parameters
        ----------
        schema : SettingSchema
            The setting schema to add.
        sync : bool
            Whether to sync the settings with the database, by default True.
        """
        await app().add_setting_schema(self.slug, schema, sync=sync)

    async def add_setting_schemas(
        self,
        schemas: list[SettingSchema],
        sync: bool = True,
    ) -> None:
        """
        Add a new settings schema to the settings manager.

        Parameters
        ----------
        schemas : list[SettingSchema]
            The schemas of the settings.
        sync : bool
            Whether to sync the settings with the database, by default True.
        """
        await app().add_setting_schemas(self.slug, schemas, sync=sync)

    def remove_setting_schema(self, key: str) -> None:
        """
        Remove a setting schema from the settings manager.

        Parameters
        ----------
        key : str
            The key of the setting.
        """
        app().remove_setting_schema(self.slug, key)

    def remove_setting_schemas(self, keys: list[str]) -> None:
        """
        Remove setting schemas from the settings manager.

        Parameters
        ----------
        keys : list[str]
            The keys of the settings.
        """
        app().remove_setting_schemas(self.slug, keys)

    def get_setting_value(
        self, key: str, default: DefaultType | None = None
    ) -> object | DefaultType | None:
        """
        Get a setting value by its source and key.

        Parameters
        ----------
        key : str
            The key of the setting.
        default : object | None
            The default value to return if the setting does not exist.

        Returns
        -------
        object | None
            The setting value with the given source and key or the default value if it does not exist.
        """
        return app().get_setting_value(source=self.slug, key=key, default=default)
