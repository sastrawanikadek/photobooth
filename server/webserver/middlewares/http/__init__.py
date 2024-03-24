"""Collection of HTTP middlewares."""

from ..interfaces import HTTPMiddlewareInterface
from .cors import CORSMiddleware
from .exception_handler import ExceptionHandlerMiddleware

DEFAULT_MIDDLEWARES: list[type[HTTPMiddlewareInterface] | HTTPMiddlewareInterface] = [
    ExceptionHandlerMiddleware,
    CORSMiddleware(origins=["http://localhost:5173"]),
]

__all__ = ["DEFAULT_MIDDLEWARES"]
