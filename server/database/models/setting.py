from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel

from server.utils.pydantic_fields import SlugStr


# Ignore mypy error until SQLModel fixed it
class Setting(SQLModel, table=True):  # type: ignore
    """
    Model and schema for a setting.

    Attributes
    ----------
    id : int
        The ID of the setting.
    slug : SlugStr
        Source of the setting.
    key : str
        The key of the setting.
    type : str
        The data type of the setting (e.g. integer, boolean, string, float).
    value : str
        The value of the setting.
    created_at : datetime
        The date and time the setting was created.
    updated_at : datetime
        The date and time the setting was last updated.
    """

    __tablename__ = "settings"

    id: int = Field(primary_key=True)
    slug: SlugStr
    key: str
    type: str
    value: str
    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()})
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )

    @property
    def parsed_value(self) -> str | bool | int | float:
        """
        Parse the value of the setting.

        Returns
        -------
        str | bool | int | float
            The parsed value of the setting.
        """
        if self.type == "boolean":
            return self.value == "true"
        elif self.type == "integer":
            return int(self.value)
        elif self.type == "float":
            return float(self.value)

        return self.value
