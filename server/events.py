from server.eventbus.event import NoDataEvent


class AppInitializedEvent(NoDataEvent):
    """Event that is fired when the app is initialized."""


class AppStartupEvent(NoDataEvent):
    """Event that is fired when the app is starting up."""


class AppReadyEvent(NoDataEvent):
    """Event that is fired when the app is ready to serve requests."""
