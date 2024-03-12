from typing import overload

from typing_extensions import Self

from server.webserver import HTTPHandlerType, RouteMethod, WebSocketHandlerType


class Route:
    """Route definition for the webserver API handlers."""

    def __init__(
        self,
        endpoint: str,
        *,
        method: RouteMethod | None = None,
        http_handler: HTTPHandlerType | None = None,
        websocket_handler: WebSocketHandlerType | None = None,
        cls: type | None = None,
        cls_method_name: str | None = None,
        is_websocket: bool = False,
        kwargs: dict[str, object] = {},
    ) -> None:
        """Initialize the route."""
        exclude_keys = ["handler", "handler_cls", "method_name"]

        self.endpoint = endpoint
        self.method = method
        self.http_handler = http_handler
        self.websocket_handler = websocket_handler
        self.cls = cls
        self.cls_method_name = cls_method_name
        self.is_websocket = is_websocket
        self.kwargs = {
            key: value for key, value in kwargs.items() if key not in exclude_keys
        }

    @classmethod
    def http_factory(
        cls, method: RouteMethod, path: str, *args: object, **kwargs: object
    ) -> Self:
        """Create a HTTP Route."""
        if len(args) == 1 and callable(args[0]):
            return cls(path, method=method, http_handler=args[0], kwargs=kwargs)
        elif len(args) == 2 and isinstance(args[0], type) and isinstance(args[1], str):
            return cls(
                path, method=method, cls=args[0], cls_method_name=args[1], kwargs=kwargs
            )
        elif "handler" in kwargs and callable(kwargs["handler"]):
            return cls(
                path, method=method, http_handler=kwargs["handler"], kwargs=kwargs
            )
        elif (
            "handler_cls" in kwargs
            and "method_name" in kwargs
            and isinstance(kwargs["handler_cls"], type)
            and isinstance(kwargs["method_name"], str)
        ):
            return cls(
                path,
                method=method,
                cls=kwargs["handler_cls"],
                cls_method_name=kwargs["method_name"],
                kwargs=kwargs,
            )

        raise TypeError("Invalid arguments")

    @overload
    @classmethod
    def http(
        cls, method: RouteMethod, path: str, handler: HTTPHandlerType, **kwargs: object
    ) -> Self:
        """Add an HTTP route."""

    @overload
    @classmethod
    def http(
        cls,
        method: RouteMethod,
        path: str,
        handler_cls: type,
        method_name: str,
        **kwargs: object,
    ) -> Self:
        """Add an HTTP route."""

    @classmethod
    def http(
        cls, method: RouteMethod, path: str, *args: object, **kwargs: object
    ) -> Self:
        """Add an HTTP route."""
        return cls.http_factory(method, path, *args, **kwargs)

    @overload
    @classmethod
    def get(
        cls,
        path: str,
        handler: HTTPHandlerType,
        *,
        name: str | None = None,
        allow_head: bool = True,
        **kwargs: object,
    ) -> Self:
        """Add a GET route."""

    @overload
    @classmethod
    def get(
        cls,
        path: str,
        handler_cls: type,
        method_name: str,
        *,
        name: str | None = None,
        allow_head: bool = True,
        **kwargs: object,
    ) -> Self:
        """Add a GET route."""

    @classmethod
    def get(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a GET route."""
        return cls.http_factory("GET", path, *args, **kwargs)

    @overload
    @classmethod
    def post(cls, path: str, handler: HTTPHandlerType, **kwargs: object) -> Self:
        """Add a POST route."""

    @overload
    @classmethod
    def post(
        cls, path: str, handler_cls: type, method_name: str, **kwargs: object
    ) -> Self:
        """Add a POST route."""

    @classmethod
    def post(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a POST route."""
        return cls.http_factory("POST", path, *args, **kwargs)

    @overload
    @classmethod
    def put(cls, path: str, handler: HTTPHandlerType, **kwargs: object) -> Self:
        """Add a PUT route."""

    @overload
    @classmethod
    def put(
        cls, path: str, handler_cls: type, method_name: str, **kwargs: object
    ) -> Self:
        """Add a PUT route."""

    @classmethod
    def put(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a PUT route."""
        return cls.http_factory("PUT", path, *args, **kwargs)

    @overload
    @classmethod
    def patch(cls, path: str, handler: HTTPHandlerType, **kwargs: object) -> Self:
        """Add a PATCH route."""

    @overload
    @classmethod
    def patch(
        cls, path: str, handler_cls: type, method_name: str, **kwargs: object
    ) -> Self:
        """Add a PATCH route."""

    @classmethod
    def patch(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a PATCH route."""
        return cls.http_factory("PATCH", path, *args, **kwargs)

    @overload
    @classmethod
    def delete(cls, path: str, handler: HTTPHandlerType, **kwargs: object) -> Self:
        """Add a DELETE route."""

    @overload
    @classmethod
    def delete(
        cls, path: str, handler_cls: type, method_name: str, **kwargs: object
    ) -> Self:
        """Add a DELETE route."""

    @classmethod
    def delete(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a DELETE route."""
        return cls.http_factory("DELETE", path, *args, **kwargs)

    @overload
    @classmethod
    def head(cls, path: str, handler: HTTPHandlerType, **kwargs: object) -> Self:
        """Add a HEAD route."""

    @overload
    @classmethod
    def head(
        cls, path: str, handler_cls: type, method_name: str, **kwargs: object
    ) -> Self:
        """Add a HEAD route."""

    @classmethod
    def head(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a HEAD route."""
        return cls.http_factory("HEAD", path, *args, **kwargs)

    @overload
    @classmethod
    def options(cls, path: str, handler: HTTPHandlerType, **kwargs: object) -> Self:
        """Add an OPTIONS route."""

    @overload
    @classmethod
    def options(
        cls, path: str, handler_cls: type, method_name: str, **kwargs: object
    ) -> Self:
        """Add an OPTIONS route."""

    @classmethod
    def options(cls, path: str, *args: object, **kwargs: object) -> Self:
        """Add a OPTIONS route."""
        return cls.http_factory("OPTIONS", path, *args, **kwargs)

    @overload
    @classmethod
    def websocket(cls, command: str, handler: WebSocketHandlerType) -> Self:
        """Add a WebSocket command handler."""

    @overload
    @classmethod
    def websocket(cls, command: str, handler_cls: type, method: str) -> Self:
        """Add a WebSocket command handler."""

    @classmethod
    def websocket(
        cls,
        command: str,
        *args: object,
        **kwargs: object,
    ) -> Self:
        """Add a WebSocket command handler."""
        if len(args) == 1 and callable(args[0]):
            return cls(
                command, websocket_handler=args[0], is_websocket=True, kwargs=kwargs
            )
        elif len(args) == 2 and isinstance(args[0], type) and isinstance(args[1], str):
            return cls(
                command,
                cls=args[0],
                cls_method_name=args[1],
                is_websocket=True,
                kwargs=kwargs,
            )
        elif "handler" in kwargs and callable(kwargs["handler"]):
            return cls(
                command,
                websocket_handler=kwargs["handler"],
                is_websocket=True,
                kwargs=kwargs,
            )
        elif (
            "handler_cls" in kwargs
            and "method_name" in kwargs
            and isinstance(kwargs["handler_cls"], type)
            and isinstance(kwargs["method_name"], str)
        ):
            return cls(
                command,
                cls=kwargs["handler_cls"],
                cls_method_name=kwargs["method_name"],
                is_websocket=True,
                kwargs=kwargs,
            )

        raise TypeError("Invalid arguments")

    def __repr__(self) -> str:
        """Get the string representation of the route."""
        if self.method is not None:
            return f"<Route method={self.method} path={self.endpoint}>"

        return f"<Route path={self.endpoint}>"
