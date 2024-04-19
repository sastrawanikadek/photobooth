from server.managers.components.models import ComponentManifest
from server.managers.settings.models import SettingSchema

from .constants import SETTING_IDLE_TIMEOUT_DURATION
from .providers import ComponentServiceProvider

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
            group="Camera",
            display="text",
            type="integer",
            default_value=300,
        )
    ],
    providers=[ComponentServiceProvider],
)
