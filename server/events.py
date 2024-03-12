from server.eventbus import Event


class AppInitializedEvent(Event):
    """Event that is fired when the app is initialized."""


class AppStartupEvent(Event):
    """Event that is fired when the app is starting up."""


class AppReadyEvent(Event):
    """Event that is fired when the app is ready to serve requests."""
