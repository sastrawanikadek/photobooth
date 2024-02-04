class CameraError(Exception):
    """Base class for camera errors."""


class ModelNotFoundError(CameraError):
    """Raised when the specified camera model is not found."""


class DeviceUSBNotFoundError(CameraError):
    """Raised when the camera is not connected to USB port."""
