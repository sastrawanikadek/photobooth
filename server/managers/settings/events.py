from server.eventbus.event import Event

from .models import SettingInfo


class SettingUpdatedEvent(Event[SettingInfo]):
    """Event for when a setting is updated."""
