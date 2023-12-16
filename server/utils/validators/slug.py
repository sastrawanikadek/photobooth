import re


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
