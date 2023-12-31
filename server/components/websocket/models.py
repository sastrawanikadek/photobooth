import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, PrivateAttr

from .interfaces import WebSocketMessagePayload


class WebSocketIncomingMessage(BaseModel):
    """
    Incoming WebSocket message.

    Attributes
    ----------
    command : str
        The command to execute.
    payload : WebSocketMessagePayload
        The payload for the command.
    timestamp : datetime
        The timestamp of the message.
    """

    command: str
    payload: WebSocketMessagePayload = None
    _timestamp: datetime = PrivateAttr(default_factory=datetime.now)


class WebSocketSuccessResponse(BaseModel):
    """
    WebSocket success response.

    Attributes
    ----------
    command : str
        The command that was executed.
    payload : WebSocketMessagePayload
        The payload for the command.
    _type : Literal["success"]
        The type of response.
    _timestamp : datetime
        The timestamp of the response.
    """

    command: str
    payload: WebSocketMessagePayload = None
    _type: Literal["success"] = "success"
    _timestamp: datetime = PrivateAttr(default_factory=datetime.now)

    def to_dict(self) -> dict[str, object]:
        """Dictionary representation of the response."""
        return {
            "command": self.command,
            "type": self._type,
            "payload": self.payload,
            "timestamp": self._timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """JSON representation of the response."""
        return json.dumps(self.to_dict())


class WebSocketErrorResponse(BaseModel):
    """
    WebSocket error response.

    Attributes
    ----------
    command : str
        The command that was executed.
    message : str
        The error message.
    _type : Literal["error"]
        The type of response.
    _timestamp : datetime
        The timestamp of the response.
    """

    command: str
    message: str
    _type: Literal["error"] = "error"
    _timestamp: datetime = PrivateAttr(default_factory=datetime.now)

    def to_dict(self) -> dict[str, object]:
        """Dictionary representation of the response."""
        return {
            "command": self.command,
            "type": self._type,
            "message": self.message,
            "timestamp": self._timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """JSON representation of the response."""
        return json.dumps(self.to_dict())
