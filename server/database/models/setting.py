from sqlmodel import Field, SQLModel


class Setting(SQLModel):
    id: int = Field(primary_key=True)
    slug: str
    key: str
    type: str
    _value: str

    def value(self) -> str | bool | int | float:
        if self.type == "boolean":
            return self._value == "true"
        elif self.type == "integer":
            return int(self._value)
        elif self.type == "float":
            return float(self._value)

        return self._value
