import re
from typing import Annotated

from pydantic import AfterValidator


def is_slug(string: str) -> bool:
    """
    Check if a string is a slug.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    bool
        True if the string is a slug, False otherwise.

    Examples
    --------
    >>> is_slug("example-component")
    True
    >>> is_slug("example_component")
    False
    """
    return re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", string) is not None


def strict_is_slug(string: str) -> bool:
    """
    Check if a string is a slug, raising a ValueError if it is not.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    bool
        True if the string is a slug

    Raises
    ------
    ValueError
        If the string is not a slug.

    Examples
    --------
    >>> strict_is_slug("example-component")
    True
    >>> strict_is_slug("example_component")
    Traceback (most recent call last):
        ...
    ValueError: example_component is not a valid slug
    """
    if not is_slug(string):
        raise ValueError(f"{string} is not a valid slug")

    return True


SlugStr = Annotated[str, AfterValidator(strict_is_slug)]
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
