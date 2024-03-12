from pydantic import BaseModel


class WebSocketSubscribeRequestDTO(BaseModel):
    channel: str


class WebSocketUnsubscribeRequestDTO(BaseModel):
    channel: str
