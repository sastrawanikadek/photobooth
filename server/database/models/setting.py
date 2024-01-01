from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel

from server.utils.pydantic_fields import SlugStr


# Ignore mypy error until SQLModel fixed it
class Setting(SQLModel, table=True):  # type: ignore
    """
    Model and schema for a setting.
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
