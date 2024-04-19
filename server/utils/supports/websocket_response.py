from server.webserver.models import (
    WebSocketErrorEnvelope,
    WebSocketMessageData,
    WebSocketResponseMessage,
)


class WebSocketResponse:
    @staticmethod
    def json(data: WebSocketMessageData = None) -> WebSocketResponseMessage:
        """Return an success response."""
        return WebSocketResponseMessage(
            status="success",
            data=data,
        )

    @staticmethod
    def empty() -> WebSocketResponseMessage:
        """Return an empty success response."""
        return WebSocketResponseMessage(
            status="success",
        )

    @staticmethod
    def error(
        message: str,
        errors: dict[str, list[str]] = {},
    ) -> WebSocketResponseMessage:
        """Return an error response."""
        return WebSocketResponseMessage(
            status="error",
            error=WebSocketErrorEnvelope(message=message, errors=errors),
        )
