from typing import Optional

from pydantic import BaseModel
from utils.validators import SlugStr


class ComponentManifest(BaseModel):
    """
    Manifest for a component.

    Attributes
    ----------
    display_name : str
        The display name of the component.
    description : str
        The description of the component.
    name : str
        The name of the component class.
    slug : str
        The id of the component.
        example: "example-component"
    """

    display_name: str
    description: str
    name: Optional[str] = None
    slug: SlugStr
