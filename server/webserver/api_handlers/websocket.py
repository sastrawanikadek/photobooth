from aiohttp import web

from ..dtos import WebSocketSubscribeRequestDTO, WebSocketUnsubscribeRequestDTO
from ..interfaces import WebServerInterface


class WebSocketAPIHandler:
    def __init__(self, webserver: WebServerInterface) -> None:
        self._webserver = webserver

    def subscribe(
        self, request: WebSocketSubscribeRequestDTO, connection: web.WebSocketResponse
    ) -> None:
        self._webserver.websocket.subscribe(request.channel, connection)

    def unsubscribe(
        self, request: WebSocketUnsubscribeRequestDTO, connection: web.WebSocketResponse
    ) -> None:
        self._webserver.websocket.unsubscribe(request.channel, connection)
