import inspect
import json
from typing import Awaitable, Callable, overload

from aiohttp import web

from server.injector import DependencyInjectorInterface
from server.utils.helpers.inspect import class_has_method

from .exception_handlers import HTTPExceptionHandler
from .interfaces import HTTPComponentInterface, HTTPHandlerType, RouteMethod
from .utils import bind_request_model, is_http_handler


class HTTPComponent(HTTPComponentInterface):
    """HTTP component for the web server."""

    def __init__(
        self,
        app: web.Application,
        injector: DependencyInjectorInterface,
        exception_handler: HTTPExceptionHandler,
    ) -> None:
        """
        Initialize the component.

        Parameters
        ----------
        app : web.Application
            The web application.
        injector : DependencyInjectorInterface
            The dependency injector.
        exception_handler : HTTPExceptionHandler
            The exception handler.
        """
        self._app = app
        self._injector = injector
        self._exception_handler = exception_handler

    def add_route(
        self, method: RouteMethod, path: str, *args: object, **kwargs: object
    ) -> None:
        """
        Add a route.

        Parameters
        ----------
        method : RouteMethod
            The HTTP method.
        path : str
            The path of the route.
        *args : object
            The arguments.
        **kwargs : object
            Additional keyword arguments.
        """
        route_method = getattr(self._app.router, f"add_{method.lower()}", None)

        if route_method is None:
            return

        if len(args) == 1 and callable(args[0]):
            route_method(path, self._inject_handler(handler=args[0]), **kwargs)
        elif len(args) == 2 and isinstance(args[0], type) and isinstance(args[1], str):
            route_method(
                path, self._inject_handler(cls=args[0], method=args[1]), **kwargs
            )
        elif "handler" in kwargs and callable(kwargs["handler"]):
            route_method(
                path, self._inject_handler(handler=kwargs["handler"]), **kwargs
            )
        elif (
            "cls" in kwargs
            and "cls_method_name" in kwargs
            and isinstance(kwargs["cls"], type)
            and isinstance(kwargs["cls_method_name"], str)
        ):
            route_method(
                path,
                self._inject_handler(
                    cls=kwargs["cls"], method=kwargs["cls_method_name"]
                ),
                **kwargs,
            )
        else:
            raise TypeError("Invalid arguments")

    @overload
    def _inject_handler(
        self, handler: HTTPHandlerType
    ) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        """
        Inject the handler with the request and required dependencies.

        Parameters
        ----------
        handler : HTTPHandlerType
            The handler to inject.

        Returns
        -------
        Callable[[web.Request], Awaitable[web.StreamResponse]]
            The injected handler.
        """

    @overload
    def _inject_handler(
        self, cls: type, method: str
    ) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        """
        Inject the handler with the request and required dependencies.

        Parameters
        ----------
        cls : type
            The class to instantiate.
        method : str
            The method to call.

        Returns
        -------
        Callable[[web.Request], Awaitable[web.StreamResponse]]
            The injected handler.
        """

    def _inject_handler(
        self,
        *_: object,
        **kwargs: object,
    ) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        """
        Inject the handler with the request and required dependencies.

        Parameters
        ----------
        *_ : object
            The arguments.
        **kwargs : object
            Additional keyword arguments.

        Returns
        -------
        Callable[[web.Request], Awaitable[web.StreamResponse]]
            The injected handler.

        Raises
        ------
        TypeError
            If the arguments are invalid.
        ValueError
            If the handler is not a valid HTTP handler.
            If the method is not found on the class.
            If the response is not an instance of web.StreamResponse.
        """
        handler_value: HTTPHandlerType | tuple[type, str]

        if "handler" in kwargs:
            if not is_http_handler(kwargs["handler"]):
                raise ValueError("Handler is not a valid HTTP handler")

            handler_value = kwargs["handler"]
        elif (
            "cls" in kwargs
            and "method" in kwargs
            and inspect.isclass(kwargs["cls"])
            and isinstance(kwargs["method"], str)
        ):
            cls = kwargs["cls"]
            method = kwargs["method"]
            handler_value = (cls, method)

            if not class_has_method(cls, method):
                raise ValueError(
                    f'Method "{method}" not found on class "{cls.__name__}"'
                )

            if not is_http_handler(getattr(cls, method)):
                raise ValueError("Method is not a valid HTTP handler")
        else:
            raise TypeError("Invalid arguments")

        return self._get_injected_handler(handler_value)

    def _get_injected_handler(
        self, handler_value: HTTPHandlerType | tuple[type, str]
    ) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        """
        Get the injected handler.

        Parameters
        ----------
        handler_value : HTTPHandlerType | tuple[type, str]
            The handler value.

        Returns
        -------
        Callable[[web.Request], Awaitable[web.StreamResponse]]
            The injected handler.
        """

        async def wrapper(request: web.Request) -> web.StreamResponse:
            with self._injector.add_temporary_container() as container:
                container.singleton(web.Request, request)

                if callable(handler_value):
                    handler = handler_value
                else:
                    cls, method = handler_value
                    instance: object = self._injector.inject_constructor(cls)
                    handler = getattr(instance, method)

                try:
                    if request.method == "GET":
                        payload = dict(request.query)
                    else:
                        try:
                            request_json = await request.json()
                            payload = (
                                request_json if isinstance(request_json, dict) else {}
                            )
                        except json.JSONDecodeError:
                            payload = {}

                    bind_request_model(container, handler, payload)

                    response = await self._injector.call_with_injection(handler)

                    if not isinstance(response, web.StreamResponse):
                        raise ValueError(
                            "Response must be instance of web.StreamResponse"
                        )
                except Exception as exc:
                    response = self._exception_handler.handle(exc, request)

                return response

        return wrapper
