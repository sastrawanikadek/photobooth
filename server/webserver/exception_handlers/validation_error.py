from http import HTTPStatus

from aiohttp import web
from pydantic import ValidationError

from server.utils.supports.http_response import HTTPResponse

from ..models import (
    WebSocketErrorEnvelope,
    WebSocketIncomingMessage,
    WebSocketResponseMessage,
)


def HTTPValidationErrorRenderer(
    exception: ValidationError,
    _: web.Request,
) -> web.StreamResponse:
    errors: dict[str, list[str]] = {}

    for error in exception.errors():
        field = ".".join([str(v) for v in error["loc"]])
        errors.setdefault(field, [])
        errors[field].append(error["msg"])

    return HTTPResponse.error(
        message="Validation Error",
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        errors=errors,
    )


def WebSocketValidationErrorRenderer(
    exception: ValidationError,
    _: web.WebSocketResponse,
    message: WebSocketIncomingMessage,
) -> WebSocketResponseMessage:
    errors: dict[str, list[str]] = {}

    for error in exception.errors():
        field = ".".join([str(v) for v in error["loc"]])
        errors.setdefault(field, [])
        errors[field].append(error["msg"])

    return WebSocketResponseMessage(
        status="error",
        command=message.command,
        error=WebSocketErrorEnvelope(
            message="Validation Error",
            errors=errors,
        ),
    )
