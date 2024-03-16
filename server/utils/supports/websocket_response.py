from server.webserver import (
    WebSocketErrorEnvelope,
    WebSocketMessageData,
    WebSocketResponseMessage,
)


class WebSocketResponse:
    @staticmethod
    def json(
        command: str, data: WebSocketMessageData = None
    ) -> WebSocketResponseMessage:
        """Return an success response."""
        return WebSocketResponseMessage(
            status="success",
            command=command,
            data=data,
        )

    @staticmethod
    def error(
        command: str,
        message: str,
        errors: dict[str, list[str]] = {},
    ) -> WebSocketResponseMessage:
        """Return an error response."""
        return WebSocketResponseMessage(
            status="error",
            command=command,
            error=WebSocketErrorEnvelope(message=message, errors=errors),
        )
