import inspect
import json
from pathlib import Path
from typing import Awaitable, Callable, overload

from aiohttp import web
from sqlmodel import SQLModel

from server.database.repository import Repository
from server.dependency_injection.interfaces import DependencyInjectorInterface
from server.utils.helpers.inspect import class_has_method
from server.utils.supports.file import File

from .interfaces import (
    ExpectHandlerType,
    HTTPComponentInterface,
    HTTPHandlerType,
    RouteMethod,
)
from .utils import bind_request_model, is_http_handler


class HTTPComponent(HTTPComponentInterface):
    """HTTP component for the web server."""

    def __init__(
        self,
        app: web.Application,
        *,
        injector: DependencyInjectorInterface,
    ) -> None:
        """
        Initialize the component.

        Parameters
        ----------
        app : web.Application
            The web application.
        injector : DependencyInjectorInterface
            The dependency injector.
        """
        self._app = app
        self._injector = injector

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

    def add_static_route(
        self,
        path: str,
        directory: str | Path,
        *,
        name: str | None = None,
        expect_handler: ExpectHandlerType | None = None,
        chunk_size: int = 256 * 1024,
        show_index: bool = False,
        follow_symlinks: bool = False,
        append_version: bool = False,
    ) -> None:
        """
        Add a route for serving static files.

        Parameters
        ----------
        path : str
            The path of the route.
        directory : str | Path
            The directory to serve files from.
        name : str | None
            The name of the route.
        expect_handler : callable[web.Request, Awaitable[web.StreamResponse | None]] | None
            The expect handler.
        chunk_size : int
            Size of single chunk for file downloading, 256Kb by default.

            Increasing chunk_size parameter to, say,
            1Mb may increase file downloading speed but consumes more memory.
        show_index : bool
            Flag for allowing to show indexes of a directory,
            by default it's not allowed and HTTP/403 will be returned on directory access.
        follow_symlinks : bool
            Flag for allowing to follow symlinks that lead outside the static root directory,
            by default it's not allowed and HTTP/404 will be returned on access
        append_version : bool
            Flag for adding file version (hash) to the url query string to avoid caching issues.
        """
        self._app.router.add_static(
            path,
            directory,
            name=name,
            expect_handler=expect_handler,
            chunk_size=chunk_size,
            show_index=show_index,
            follow_symlinks=follow_symlinks,
            append_version=append_version,
        )

    def get_route(self, name: str) -> web.AbstractResource | None:
        """
        Get the route by name.

        Parameters
        ----------
        name : str
            The name of the route.

        Returns
        -------
        web.AbstractResource | None
            The route with the given name or None if not found.
        """
        return self._app.router.get(name)

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

                payload = await self._parse_request_payload(request)
                bind_request_model(container, handler, payload)

                named_deps = await self._resolve_variable_path(request, handler)

                response = await self._injector.call_with_injection(handler, named_deps)

                if not isinstance(response, web.StreamResponse):
                    raise ValueError("Response must be instance of web.StreamResponse")

                return response

        return wrapper

    async def _parse_request_payload(self, request: web.Request) -> dict[str, object]:
        """
        Parse the request payload based on the request method or content type.

        Parameters
        ----------
        request : web.Request
            The request object.

        Returns
        -------
        dict[str, object]
            The request payload.
        """
        if request.method == "GET":
            return dict(request.query)

        if request.content_type == "multipart/form-data":
            data = await request.post()
            request_body: dict[str, object] = {}

            for key, value in data.items():
                if isinstance(value, web.FileField):
                    request_body[key] = self._injector.inject_constructor(
                        File, named_deps={"file": value}
                    )
                else:
                    request_body[key] = value

            return request_body

        try:
            request_json = await request.json()
            return request_json if isinstance(request_json, dict) else {}
        except json.JSONDecodeError:
            return {}

    async def _resolve_variable_path(
        self, request: web.Request, handler: HTTPHandlerType
    ) -> dict[str, object]:
        """
        Resolve the variable path parameters.

        Parameters
        ----------
        request : web.Request
            The request object.
        handler : HTTPHandlerType
            The handler to resolve the variable path for.

        Returns
        -------
        dict[str, object]
            Resolved dependency for the variable path.
        """
        parameters = inspect.signature(handler).parameters
        dependencies: dict[str, object] = {}

        for pathname, value in request.match_info.items():
            resolver_name = "find"

            if "__" in pathname:
                pathname, attribute = pathname.split("__")
                resolver_name = f"find_by_{attribute}"

            if pathname not in parameters:
                continue

            annotation = parameters[pathname].annotation

            if annotation == int:
                dependencies[pathname] = int(value)
            elif annotation == float:
                dependencies[pathname] = float(value)
            elif issubclass(annotation, SQLModel):
                dependencies[pathname] = await self._resolve_path_model(
                    annotation,
                    resolver_name,
                    value,
                )
            else:
                dependencies[pathname] = value

        return dependencies

    async def _resolve_path_model(
        self, model: type[SQLModel], resolver_name: str, value: str
    ) -> SQLModel:
        """
        Resolve the path model.

        Parameters
        ----------
        model : type[SQLModel]
            The model to resolve.
        resolver_name : str
            The method name in the repository to resolve the model.
        value : str
            The value to resolve.

        Returns
        -------
        SQLModel
            The resolved model.
        """
        if not hasattr(model, "get_repository"):
            raise AttributeError('Model does not have a "get_repository" method.')

        repository_cls = model.get_repository()

        if not issubclass(repository_cls, Repository):
            raise ValueError(
                'Return of "get_repository" method must be a subclass of Repository'
            )

        if not class_has_method(repository_cls, resolver_name):
            raise AttributeError(f"Method '{resolver_name}' not found on repository")

        repository = self._injector.inject_constructor(repository_cls)
        return await getattr(repository, resolver_name)(value)
