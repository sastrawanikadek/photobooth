import inspect
from typing import Callable, TypeVar, cast

from aiohttp import web

from server.utils.helpers.inspect import has_same_signature
from server.utils.supports.http_response import HTTPResponse

ExceptionType = TypeVar("ExceptionType", bound=Exception)
Handler = Callable[[Exception, web.Request], web.StreamResponse | None]


class HTTPExceptionHandler:
    """Exception handler for HTTP connection."""

    _renderers: dict[type[Exception], Handler] = {}

    def render(
        self,
        handler: Callable[[ExceptionType, web.Request], web.StreamResponse | None],
    ) -> None:
        """Register a renderer for the exception."""
        signature = inspect.signature(handler)
        parameters = list(signature.parameters.values())

        exception_type = parameters[0].annotation

        if not issubclass(exception_type, Exception):
            raise TypeError("Invalid arguments")

        self._renderers[exception_type] = cast(Handler, handler)

    def handle(
        self, exception: ExceptionType, request: web.Request
    ) -> web.StreamResponse:
        """Handle an exception."""
        if hasattr(exception, "http_render") and callable(exception.http_render):
            same_signature = has_same_signature(
                exception.http_render,
                [web.Request],
                web.StreamResponse,
            )

            if same_signature:
                return exception.http_render(request)

        renderer = self._renderers.get(type(exception))

        if renderer is None:
            for exception_cls, handler in self._renderers.items():
                if issubclass(type(exception), exception_cls):
                    renderer = handler
                    break

        response = None if renderer is None else renderer(exception, request)

        if response is None:
            response = HTTPResponse.error(message="Internal Server Error")

        return response
