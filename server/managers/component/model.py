from pydantic import BaseModel, Field

from server.managers.settings import SettingSchema
from server.providers import ServiceProvider
from server.utils.pydantic_fields import SlugStr


class ComponentManifest(BaseModel):
    """
    Manifest for a component.

    Attributes
    ----------
    display_name : str
        The display name of the component.
    description : str
        The description of the component.
    slug : str
        The id of the component.
        example: "example-component"
    preinstalled : bool
        Whether the component is preinstalled or not.
    name : str
        The name of the component class.
        example: "ExampleComponent"
    requirements : dict[str, str]
        Additional module that the component requires.
    settings : list[SettingSchema]
        The settings that the component provides.
    providers : list[type[ServiceProvider]]
        Service providers that the component provides.
    """

    display_name: str = Field(..., alias="displayName")
    description: str
    slug: SlugStr
    preinstalled: bool = False
    name: str | None = None
    requirements: dict[str, str] | None = None
    settings: list[SettingSchema] = []
    providers: list[type[ServiceProvider]] = []
