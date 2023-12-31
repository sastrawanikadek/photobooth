class WebSocketHandlerError(Exception):
    """
    Raised when an error occurs in the command handler.

    Attributes
    ----------
    message : str
        The error message.
    """

    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
