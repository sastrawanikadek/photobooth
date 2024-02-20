from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class CameraWidget:
    """Base class for camera widgets."""

    id: str
    name: str
    label: str
    type: str
    value: object


@dataclass(frozen=True)
class TextWidget(CameraWidget):
    """A text widget."""

    type: str = field(default="text", init=False)
    value: str


@dataclass(frozen=True)
class RadioWidget(CameraWidget):
    """A radio widget."""

    type: str = field(default="radio", init=False)
    value: str
    options: list[str]


@dataclass(frozen=True)
class ToggleWidget(CameraWidget):
    """A toggle widget."""

    type: str = field(default="toggle", init=False)
    value: Literal[0, 1]
