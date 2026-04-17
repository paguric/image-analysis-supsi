from pydantic import BaseModel
from app.models.enums import Analisi


class RoiData(BaseModel):
    index: int
    frame: int


class RoiResponse(BaseModel):
    id: int | None
    idx: int
    video_path: str
    fase: Analisi
    center_x: int | None = None
    center_y: int | None = None
    has_contours: bool = False
    contours: list[list[int]] | None = None  # Lista di punti [[x1,y1], [x2,y2], ...]
