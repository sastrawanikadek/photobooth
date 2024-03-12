import json
from typing import Literal

import pendulum
from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import DateTime

from server.utils.supports.encoder import JSONEncoder

from .interfaces import WebSocketMessageData


class WebSocketIncomingMessage(BaseModel):
    """
    Incoming WebSocket message.

    Attributes
    ----------
    command : str
        The command to execute.
    payload : WebSocketMessageData
        The payload for the command.
    timestamp : DateTime
        The timestamp of the message.
    """

    command: str
    payload: WebSocketMessageData = None
    timestamp: DateTime = Field(default_factory=pendulum.now, init_var=False)


class WebSocketErrorEnvelope(BaseModel):
    """
    Error envelope for WebSocket response message.

    Attributes
    ----------
    message : str
        The message of the response.
    errors : dict[str, list[str]]
        Detail of the error.
    """

    message: str
    errors: dict[str, list[str]] | None = None


class WebSocketResponseMessage(BaseModel):
    """
    WebSocket response message.

    Attributes
    ----------
    status : Literal["success", "error"]
        The status of the response.
    command : str
        The command that was executed.
    data : WebSocketMessageData | None
        The data for the command if any.
    error : WebSocketErrorEnvelope | None
        The error for the command if any.
    timestamp : DateTime
        The timestamp of the response.
    """

    status: Literal["success", "error"]
    command: str
    data: WebSocketMessageData = None
    error: WebSocketErrorEnvelope | None = None
    timestamp: DateTime = Field(default_factory=pendulum.now, init_var=False)

    def to_json(self) -> str:
        """JSON representation of the response."""
        return json.dumps(self, cls=JSONEncoder)


class WebSocketBroadcastMessage(BaseModel):
    """
    WebSocket broadcast message.

    Attributes
    ----------
    channel : str
        The channel to broadcast to.
    payload : WebSocketMessageData
        The payload for the command.
    timestamp : DateTime
        The timestamp of the message.
    """

    channel: str
    payload: WebSocketMessageData
    timestamp: DateTime = Field(default_factory=pendulum.now, init_var=False)

    def to_json(self) -> str:
        """JSON representation of the response."""
        return json.dumps(self, cls=JSONEncoder)
