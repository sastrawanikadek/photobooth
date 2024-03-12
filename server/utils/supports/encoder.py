import json

import pendulum
from pydantic import BaseModel


class JSONEncoder(json.JSONEncoder):
    def default(self, o: object) -> object:
        if hasattr(o, "__serialize__") and callable(o.__serialize__):
            return o.__serialize__()

        if isinstance(o, BaseModel):
            return o.model_dump(exclude_none=True, by_alias=True)

        if isinstance(o, pendulum.DateTime):
            return o.to_iso8601_string()

        return super().default(o)
