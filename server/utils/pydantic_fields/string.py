from typing import Annotated

from pydantic import AfterValidator

from server.utils.validators import is_slug


def _check_slug(string: str) -> str:
    """
    Check if a string is a slug.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    str
        The string if it is a slug.

    Raises
    ------
    ValueError
        If the string is not a slug.

    Examples
    --------
    >>> check_slug("example-component")
    "example-component"
    >>> check_slug("example_component")
    Traceback (most recent call last):
        ...
    ValueError: example_component is not a valid slug
    """
    if not is_slug(string):
        raise ValueError(f"{string} is not a valid slug")

    return string


SlugStr = Annotated[str, AfterValidator(_check_slug)]
"""
An annotated string that must be a valid slug.

A slug is a string that contains only lowercase letters, numbers, and hyphens, and
cannot start or end with a hyphen. Slugs are used to identify components.

Examples
--------
>>> from pydantic import BaseModel
>>> class Model(BaseModel):
...     slug: SlugStr
...
>>> Model(slug="example-component")
Model(slug='example-component')
>>> Model(slug="example_component")
Traceback (most recent call last):
    ...
pydantic.error_wrappers.ValidationError: 1 validation error for Model
slug
  example_component is not a valid slug (type=value_error)
"""
