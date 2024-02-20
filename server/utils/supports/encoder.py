import json

from pydantic import BaseModel

from .collection import Collection


class JSONEncoder(json.JSONEncoder):
    def default(self, o: object) -> object:
        if isinstance(o, BaseModel):
            return o.model_dump()

        if isinstance(o, Collection):
            return o.to_list()

        return super().default(o)
