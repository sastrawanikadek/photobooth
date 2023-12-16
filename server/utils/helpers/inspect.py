import inspect
from typing import Callable, Optional, TypeVar, cast

_RT = TypeVar("_RT")
_ST = TypeVar("_ST", bound=type)


def get_first_match_signature(
    callable: Callable[..., _RT], signature: _ST
) -> Optional[_ST]:
    """
    Get the first matching subtype of a signature from a callable.

    Parameters
    ----------
    callable : callable
        The callable to get the signature from.
    signature : type
        The signature to match.

    Returns
    -------
    Optional[type]
        The first matching subtype of the signature or None if no match was found.
    """
    parameters = inspect.signature(callable).parameters

    for parameter in parameters.values():
        if issubclass(parameter.annotation, signature):
            return cast(_ST, parameter.annotation)

    return None
