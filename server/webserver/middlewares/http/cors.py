from aiohttp import web

from ..interfaces import HTTPMiddlewareHandler, HTTPMiddlewareInterface

DEFAULT_ALLOWED_HEADERS = [
    "Accept",
    "Accept-Encoding",
    "Accept-Language",
    "Authorization",
    "Content-Type",
    "Origin",
    "User-Agent",
    "X-Requested-With",
]

DEFAULT_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


class CORSMiddleware(HTTPMiddlewareInterface):
    """Middleware to handle CORS."""

    def __init__(
        self,
        origins: list[str] = ["*"],
        expose_headers: list[str] = [],
        allow_headers: list[str] = DEFAULT_ALLOWED_HEADERS,
        allow_methods: list[str] = DEFAULT_ALLOWED_METHODS,
        allow_credentials: bool = False,
        max_age: int = 600,
    ) -> None:
        """Initialize the middleware."""
        self._origins = origins
        self._expose_headers = expose_headers
        self._allow_headers = allow_headers
        self._allow_methods = allow_methods
        self._allow_credentials = allow_credentials
        self._max_age = max_age

    async def handle(
        self, request: web.Request, handler: HTTPMiddlewareHandler
    ) -> web.StreamResponse:
        """Handle the request."""
        is_preflight = (
            request.method == "OPTIONS"
            and "Access-Control-Request-Method" in request.headers
        )

        if is_preflight:
            response = web.Response()
        else:
            response = await handler(request)

        origin = request.headers.get("Origin")

        if not origin:
            return response

        if self._origins != ["*"] and origin not in self._origins:
            return response

        if self._allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        if self._origins == ["*"] and not self._allow_credentials:
            response.headers["Access-Control-Allow-Origin"] = "*"
        else:
            response.headers["Access-Control-Allow-Origin"] = origin

        if self._expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(
                self._expose_headers
            )

        if request.method == "OPTIONS":
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                self._allow_methods
            )
            response.headers["Access-Control-Allow-Headers"] = ", ".join(
                self._allow_headers
            )
            response.headers["Access-Control-Max-Age"] = str(self._max_age)

        return response
