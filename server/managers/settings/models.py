from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator
from pydantic import Field as PydanticField
from sqlalchemy import func
from sqlmodel import Field, SQLModel
from typing_extensions import Self

from server.utils.pydantic_fields import SlugStr

Display = Literal[
    "text",
    "textarea",
    "select",
    "checkbox",
    "radio",
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
    source : SlugStr
        The source of the setting, it can be "system" or component slug.
    key : str
        Unique identifier of the setting.
    value : str | None
        The value of the setting.
    created_at : datetime
        The date and time the setting was created.
    updated_at : datetime
        The date and time the setting was last updated.
    """

    __tablename__ = "settings"

    id: int | None = Field(None, primary_key=True)
    source: SlugStr
    key: str
    value: str | None = None
    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()})
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


class BackupSetting(SQLModel, table=True):  # type: ignore
    """
    Model for a backup setting table in the database.

    Attributes
    ----------
    id : int | None
        The ID of the setting.
    source : SlugStr
        The source of the setting, it can be "system" or component slug.
    key : str
        Unique identifier of the setting.
    value : str | None
        The value of the setting.
    created_at : datetime
        The date and time the setting was created.
    updated_at : datetime
        The date and time the setting was last updated.
    """

    __tablename__ = "backup_settings"

    id: int | None = Field(None, primary_key=True)
    source: SlugStr
    key: str
    value: str | None = None
    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()})
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


class SettingOption(BaseModel):
    """
    Model for a setting option which is used in setting that has
    select, checkbox, or radio display.

    Attributes
    ----------
    label : str
        The label of the option.
    value : object
        The value of the option.
    """

    label: str
    value: object


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
    options : list[SettingOption]
        The options of the setting if it has select, checkbox, or radio display.
    description : str
        The description of the setting.
    """

    key: str
    title: str
    display: Display
    type: ValueType
    default_value: object | None = PydanticField(None, alias="defaultValue")
    options: list[SettingOption] = []
    description: str | None = None

    @model_validator(mode="before")
    @classmethod
    def check_options_presence(cls, data: object) -> object:
        """Check if the setting has options when it has select, checkbox, or radio display."""
        if isinstance(data, dict):
            if "key" in data and "display" in data:
                if (
                    data["display"] in ["select", "checkbox", "radio"]
                    and "options" not in data
                ):
                    raise ValueError(f"Setting \"{data['key']}\" must have options")
                elif (
                    data["display"] not in ["select", "checkbox", "radio"]
                    and "options" in data
                ):
                    raise ValueError(f"Setting \"{data['key']}\" must not have options")
        return data

    @model_validator(mode="after")
    def check_default_value(self) -> Self:
        """Check if the default value type is the same as the setting type."""
        if (
            self.default_value is not None
            and type(self.default_value) is not type_mapping[self.type]
        ):
            raise ValueError(
                f'Default value type of setting "{self.key}" must be {self.type}'
            )
        return self

    @model_validator(mode="after")
    def check_options_value(self) -> Self:
        """Check if the options value type is the same as the setting type."""
        for option in self.options:
            if type(option.value) is not type_mapping[self.type]:
                raise ValueError(
                    f'Option value type of setting "{self.key}" must be {self.type}',
                )
        return self


class SettingInfo(SettingSchema):
    """
    Model with complete information of a setting.

    Attributes
    ----------
    id : int
        The ID of the setting.
    source : SlugStr
        The source of the setting, it can be "system" or component slug.
    value : object
        The value of the setting.
    """

    id: int
    source: SlugStr
    value: object | None = None

    @model_validator(mode="after")
    def check_value_type(self) -> Self:
        """Check if the value type is the same as the setting type."""
        if self.value is not None and type(self.value) is not type_mapping[self.type]:
            raise ValueError(f'Value type of setting "{self.id}" must be {self.type}')
        return self
