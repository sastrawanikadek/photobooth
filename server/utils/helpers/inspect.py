import inspect
from typing import Callable, TypeVar, cast

_RT = TypeVar("_RT")
_ST = TypeVar("_ST", bound=type)


def get_first_match_signature(
    callable: Callable[..., _RT], signature: _ST
) -> _ST | None:
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
    type | None
        The first matching subtype of the signature or None if no match was found.
    """
    parameters = inspect.signature(callable).parameters

    for parameter in parameters.values():
        if issubclass(parameter.annotation, signature):
            return cast(_ST, parameter.annotation)

    return None


def has_same_signature(
    callable: Callable[..., object], parameters: list[object], return_annotation: object
) -> bool:
    """
    Check if the given callable has exactly the same signature.

    Parameters
    ----------
    callable : callable
        The callable to check.
    parameters : list
        List of parameter annotations.
    return_annotation : object
        Type of the return.

    Returns
    -------
    bool
        True if the callable has exactly the same signature, otherwise False.
    """
    signature = inspect.signature(callable)
    callable_parameters = [
        parameter.annotation for parameter in signature.parameters.values()
    ]

    return (
        callable_parameters == parameters
        and signature.return_annotation == return_annotation
    )


def class_has_method(cls: type, method: str) -> bool:
    """
    Check if the class has the given method.

    Parameters
    ----------
    cls : type
        The class to check.
    method : str
        The method to check.

    Returns
    -------
    bool
        True if the class has the method, otherwise False.
    """
    return hasattr(cls, method) and callable(getattr(cls, method))
