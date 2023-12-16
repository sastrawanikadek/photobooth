"""Component for managing WebSocket connections and handling WebSocket messages."""

from .component import WebSocket
from .constants import SLUG
from .interfaces import WebSocketInterface

__all__ = ["WebSocket", "WebSocketInterface", "SLUG"]
