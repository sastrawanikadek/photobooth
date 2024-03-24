import inspect
from typing import Callable, TypeGuard

from aiohttp import web
from pydantic import BaseModel

from server.injector import DependencyContainerInterface
from server.utils.helpers.inspect import get_first_match_signature

from .interfaces import HTTPHandlerType, WebSocketHandlerType
from .models import WebSocketResponseMessage


def bind_request_model(
    container: DependencyContainerInterface,
    handler: Callable[..., object],
    payload: dict[str, object],
) -> None:
    """
    Bind Pydantic model which contains request data to the container.

    Parameters
    ----------
    container : DependencyContainerInterface
        The dependency container.
    handler : Callable[..., object]
        The handler.
    payload : dict[str, object]
        The request payload.
    """
    model = get_first_match_signature(handler, BaseModel)

    if model is None:
        return

    instance = model(**payload)
    container.singleton(model, instance)


def is_websocket_handler(handler: object) -> TypeGuard[WebSocketHandlerType]:
    """
    Check if the given handler is a WebSocket handler.

    Parameters
    ----------
    handler : object
        The handler to check.

    Returns
    -------
    TypeGuard[WebSocketHandlerType]
        True if the handler is a WebSocket handler, otherwise False.
    """
    if not callable(handler):
        return False

    signature = inspect.signature(handler)
    return_type = signature.return_annotation

    return inspect.isclass(return_type) and issubclass(
        return_type, WebSocketResponseMessage
    )


def is_http_handler(handler: object) -> TypeGuard[HTTPHandlerType]:
    """
    Check if the given handler is an HTTP handler.

    Parameters
    ----------
    handler : object
        The handler to check.

    Returns
    -------
    TypeGuard[HTTPHandlerType]
        True if the handler is an HTTP handler, otherwise False.
    """
    if not callable(handler):
        return False

    signature = inspect.signature(handler)
    return_type = signature.return_annotation

    return inspect.isclass(return_type) and issubclass(return_type, web.StreamResponse)
