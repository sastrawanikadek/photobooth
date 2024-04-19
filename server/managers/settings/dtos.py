from pydantic import BaseModel

from server.utils.supports.file import File


class UpdateSettingRequestDTO(BaseModel):
    value: str | File
