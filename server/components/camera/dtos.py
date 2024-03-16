from pydantic import BaseModel


class CameraCaptureResponseDTO(BaseModel):
    image: str
