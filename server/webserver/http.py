import inspect
from typing import Awaitable, Callable, overload

from aiohttp import web

from server.injector import DependencyInjectorInterface

from .exception_handlers import HTTPExceptionHandler
from .interfaces import HTTPComponentInterface, HTTPHandlerType, RouteMethod


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
            If the method is not found on the class or
            if the response is not an instance of web.StreamResponse.
        """

        async def wrapper(request: web.Request) -> web.StreamResponse:
            with self._injector.add_temporary_container() as container:
                container.singleton(web.Request, request)

                if "handler" in kwargs and callable(kwargs["handler"]):
                    response = await self._injector.call_with_injection(
                        kwargs["handler"]
                    )
                elif (
                    "cls" in kwargs
                    and "method" in kwargs
                    and inspect.isclass(kwargs["cls"])
                    and isinstance(kwargs["method"], str)
                ):
                    instance: object = self._injector.inject_constructor(kwargs["cls"])

                    if not hasattr(kwargs["cls"], kwargs["method"]):
                        raise ValueError(
                            f'Method "{kwargs["method"]}" not found on class "{kwargs["cls"].__name__}"'
                        )

                    response = await self._injector.call_with_injection(
                        getattr(instance, kwargs["method"])
                    )
                else:
                    raise TypeError("Invalid arguments")

                if not isinstance(response, web.StreamResponse):
                    raise ValueError("Response must be instance of web.StreamResponse")

                return response

        return wrapper
