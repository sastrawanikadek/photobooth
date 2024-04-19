import typing
from datetime import datetime
from typing import Literal

from pydantic import UUID5, BaseModel, model_validator
from pydantic import Field as PydanticField
from sqlalchemy import func
from sqlmodel import Field, SQLModel
from typing_extensions import Self

from server.utils.helpers.pydantic import validation_error
from server.utils.helpers.serialization import json_deserialize
from server.utils.pydantic_fields import SlugStr

if typing.TYPE_CHECKING:
    from .repositories import SettingsRepository

from .utils import generate_setting_uuid, is_valid_value, is_value_match_option

Display = Literal[
    "text",
    "textarea",
    "select",
    "checkbox",
    "radio",
    "toggle",
]

ValueType = Literal[
    "integer",
    "boolean",
    "string",
    "float",
    "list",
]

type_mapping = {
    "integer": int,
    "boolean": bool,
    "string": str,
    "float": float,
    "list": list,
}


class Setting(SQLModel, table=True):  # type: ignore
    """
    Model for a setting table in the database.

    Attributes
    ----------
    id : int | None
        The ID of the setting.
    uuid : UUID5
        The UUID of the setting.
    source : SlugStr
        The source of the setting, it can be "system" or component slug.
    key : str
        Unique identifier of the setting.
    value : str | None
        The value of the setting in JSON string format.
    created_at : datetime
        The date and time the setting was created.
    updated_at : datetime
        The date and time the setting was last updated.
    """

    __tablename__ = "settings"

    id: int | None = Field(None, primary_key=True)
    uuid: UUID5 = Field(..., unique=True)
    source: SlugStr
    key: str
    value: str | None = None
    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()})
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )

    @property
    def parsed_value(self) -> object:
        """Parse the value from JSON string to object."""
        return json_deserialize(self.value)

    @staticmethod
    def get_repository() -> type["SettingsRepository"]:
        """Get the repository for the model."""
        from .repositories import SettingsRepository

        return SettingsRepository


class SettingOption(BaseModel):
    """
    Model for a setting option which is used in setting that has
    select, checkbox, or radio display.

    Attributes
    ----------
    label : str
        The label of the option.
    value : str
        The value of the option.
    """

    label: str
    value: str


class SettingSchema(BaseModel):
    """
    Schema for a setting.

    Attributes
    ----------
    key : str
        Unique identifier of the setting.
    title : str
        The title of the setting.
    display : Display
        Display type of the setting.
    type : ValueType
        Data type of the setting (e.g. integer, boolean, string, float).
    default_value : object
        The default value of the setting.
    options : list[str] | list[SettingOption]
        The options of the setting if it has select, checkbox, or radio display.
    description : str
        The description of the setting.
    condition : str
        The condition when the setting is visible.
    group : str
        The group of the setting.
    """

    key: str
    title: str
    group: str
    display: Display
    type: ValueType
    default_value: object | None = PydanticField(
        None, serialization_alias="defaultValue"
    )
    options: list[str] | list[SettingOption] | None = None
    description: str | None = None
    condition: str | None = None

    @property
    def has_options(self) -> bool:
        """Check if the setting has options."""
        return self.display in ["select", "checkbox", "radio"]

    @model_validator(mode="before")
    @classmethod
    def check_options_presence(cls, data: object) -> object:
        """Check if the setting has options when it has select, checkbox, or radio display."""
        if isinstance(data, dict):
            if "title" in data and "display" in data:
                if data["display"] in ["select", "checkbox", "radio"] and not data.get(
                    "options"
                ):
                    raise ValueError(f"Setting \"{data['title']}\" must have options")
                elif data["display"] not in [
                    "select",
                    "checkbox",
                    "radio",
                ] and data.get("options"):
                    raise ValueError(
                        f"Setting \"{data['title']}\" must not have options"
                    )
        return data

    @model_validator(mode="after")
    def check_default_value(self) -> Self:
        """Check if the default value type is the same as the setting type."""
        if not is_valid_value(self.type, self.default_value):
            raise ValueError(
                f'Default value type of setting "{self.title}" must be {self.type} not {type(self.default_value).__name__}'
            )
        return self

    @model_validator(mode="after")
    def check_options_value(self) -> Self:
        """Check if the options value type is the same as the setting type."""
        for option in self.options or []:
            if (isinstance(option, str) and self.type != "string") or (
                isinstance(option, SettingOption)
                and not is_valid_value(self.type, option.value, required=True)
            ):
                raise ValueError(
                    f'Option value type of setting "{self.title}" must be {self.type}',
                )
        return self


class SettingInfo(SettingSchema, validate_assignment=True):
    """
    Model with complete information of a setting.

    Attributes
    ----------
    uuid : UUID5
        The UUID of the setting.
    source : SlugStr
        The source of the setting, it can be "system" or component slug.
    value : object
        The value of the setting.
    """

    uuid: UUID5
    source: SlugStr
    value: object | None = None

    @model_validator(mode="after")
    def check_value_type(self) -> Self:
        """Check if the value type is the same as the setting type."""
        if self.has_options and self.value is not None:
            if not is_value_match_option(self.options, self.value):
                raise validation_error(
                    field="value",
                    message=f'Value of setting "{self.title}" must match one of the options',
                    input=self.value,
                )

        if not is_valid_value(self.type, self.value):
            raise validation_error(
                field="value",
                message=f'Value type of setting "{self.title}" must be {self.type}',
                input=self.value,
            )
        return self

    @model_validator(mode="after")
    def check_uuid(self) -> Self:
        """Check if the UUID is valid."""
        valid_uuid = generate_setting_uuid(self.source, self.key)

        if self.uuid is None or self.uuid != valid_uuid:
            raise ValueError(f'UUID of setting "{self.title}" is invalid')

        return self
