import asyncio
from typing import Awaitable, Callable, TypeVar, cast

_RT = TypeVar("_RT", bound=object)


async def safe_invoke(
    func: Callable[..., _RT | Awaitable[_RT]],
    *args: tuple[object],
    **kwargs: dict[str, object],
) -> _RT:
    """
    Safely invoke a function and return the result.

    If the function is a coroutine function, it will be awaited.

    Parameters
    ----------
    func : callable
        The function to invoke.
    args : tuple
        The positional arguments to pass to the function.
    kwargs : dict
        The keyword arguments to pass to the function.

    Returns
    -------
    _RT
        The result of the function.
    """
    if asyncio.iscoroutinefunction(func):
        return cast(_RT, await func(*args, **kwargs))

    return cast(_RT, func(*args, **kwargs))


async def safe_invokes(
    funcs: list[Callable[..., _RT | Awaitable[_RT]]],
    *args: tuple[object],
    **kwargs: dict[str, object],
) -> list[_RT]:
    """
    Safely invoke a list of functions and return the results.

    Parameters
    ----------
    funcs : list[callable]
        The functions to invoke.
    args : tuple
        The positional arguments to pass to the functions.
    kwargs : dict
        The keyword arguments to pass to the functions.

    Returns
    -------
    list[_RT]
        The results of the functions.
    """
    return await asyncio.gather(
        *[safe_invoke(func, *args, **kwargs) for func in funcs],
    )
