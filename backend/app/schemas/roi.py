from pydantic import BaseModel


class RoiData(BaseModel):
    index: int
    frame: int
