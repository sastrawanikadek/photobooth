from server.webserver import (
    WebSocketErrorEnvelope,
    WebSocketMessageData,
    WebSocketResponseMessage,
)


class WebSocketResponse:
    @staticmethod
    def json(command: str, data: WebSocketMessageData = None) -> str:
        """Return a JSON success response."""
        return WebSocketResponseMessage(
            status="success",
            command=command,
            data=data,
        ).to_json()

    @staticmethod
    def error(
        command: str,
        message: str,
        errors: dict[str, list[str]] = {},
    ) -> str:
        """Return an JSON error response."""
        return WebSocketResponseMessage(
            status="error",
            command=command,
            error=WebSocketErrorEnvelope(message=message, errors=errors),
        ).to_json()
