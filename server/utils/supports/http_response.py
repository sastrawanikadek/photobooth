from http import HTTPStatus

from aiohttp import typedefs, web

from server.utils.helpers.serialization import json_serialize


class HTTPResponse:
    @staticmethod
    def json(
        status: int = HTTPStatus.OK,
        data: object | None = None,
        headers: typedefs.LooseHeaders | None = None,
    ) -> web.StreamResponse:
        """Return a JSON response."""
        content = json_serialize({"data": data})

        return web.Response(
            text=content if status != HTTPStatus.NO_CONTENT else None,
            content_type="application/json",
            status=status,
            headers=headers,
        )

    @staticmethod
    def empty(
        headers: typedefs.LooseHeaders | None = None,
    ) -> web.StreamResponse:
        """Return an empty response."""
        return web.Response(
            status=HTTPStatus.NO_CONTENT,
            headers=headers,
        )

    @staticmethod
    def error(
        message: str,
        status: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        errors: dict[str, list[str]] = {},
        headers: typedefs.LooseHeaders | None = None,
    ) -> web.StreamResponse:
        """Return an error response."""
        content = json_serialize(
            {
                "error": {
                    "code": status,
                    "message": message,
                    "errors": errors,
                }
            }
        )

        return web.Response(
            text=content,
            content_type="application/json",
            status=status,
            headers=headers,
        )
