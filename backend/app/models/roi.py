import io
import enum
import cv2
import numpy as np
from typing import List, Optional

from app.services import cv2_service

from sqlmodel import Field, SQLModel, Column, Relationship, Enum as SAEnum
from pydantic import ConfigDict
from sqlalchemy import LargeBinary
from sqlalchemy.orm import relationship


class Analisi(str, enum.Enum):
    PRIMA = "prima"
    DOPO = "dopo"


class Roi(SQLModel, table=True):
    __tablename__ = "roi"

    id: int | None = Field(default=None, primary_key=True)
    # pipeline = relationship(back_populates="roi")
    pipelines: List["Pipeline"] = Relationship(back_populates="roi")

    idx: int
    video_path: str
    fase: Analisi = Field(default=None, sa_column=Column(SAEnum(Analisi)))

    # Colonna binaria grezza sul DB
    contours_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

    # Abilitazione tipi arbitrari calcolati on-demand
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def contours(self) -> np.ndarray | None:
        if self.contours_data is None:
            return None
        buffer = io.BytesIO(self.contours_data)
        return np.load(buffer, allow_pickle=False)

    @contours.setter
    def contours(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.contours_data = buffer.getvalue()

    def get_center(self) -> tuple[int, int]:
        (cx, cy), _ = cv2.minEnclosingCircle(self.contours)
        return (int(cx), int(cy))

    def get_pixels(self, frame: int) -> np.ndarray:
        img = cv2_service.extract_frame(self.video_path, frame)
        (cx, cy), radius = cv2.minEnclosingCircle(self.contours)
        return cv2.getRectSubPix(img, (int(2 * radius), int(2 * radius)), (cx, cy))
