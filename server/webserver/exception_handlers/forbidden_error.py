from http import HTTPStatus

from aiohttp import web

from server.utils.supports.http_response import HTTPResponse


def http_forbidden_error_renderer(
    exception: web.HTTPForbidden,
    _: web.Request,
) -> web.StreamResponse:
    return HTTPResponse.error(
        message=str(exception) or "You are not allowed to access this resource.",
        status=HTTPStatus.FORBIDDEN,
    )
