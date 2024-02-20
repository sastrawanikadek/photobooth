from server.managers.component import ComponentManifest
from server.managers.settings import SettingSchema

from .constants import SETTING_IDLE_TIMEOUT_DURATION
from .providers import WebSocketRoutesServiceProvider

__MANIFEST__ = ComponentManifest(
    displayName="Camera",
    description="Component for interacting with a camera device.",
    slug="camera",
    preinstalled=True,
    requirements={"gphoto2": "2.5.0"},
    settings=[
        SettingSchema(
            key=SETTING_IDLE_TIMEOUT_DURATION,
            title="Idle Timeout Duration",
            description="The camera's duration of inactivity in seconds before it turns off.",
            display="text",
            type="integer",
            default_value=300,
        )
    ],
    providers=[WebSocketRoutesServiceProvider],
)
