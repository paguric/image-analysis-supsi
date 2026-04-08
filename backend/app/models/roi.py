import io
import enum
import cv2
import numpy as np
from typing import List

from app.services import cv2_service

from sqlmodel import Field, SQLModel, Column, Relationship, Enum as SAEnum
from pydantic import ConfigDict
from sqlalchemy import LargeBinary


class Analisi(str, enum.Enum):
    PRIMA = "prima"
    DOPO = "dopo"


class Roi(SQLModel, table=True):
    __tablename__ = "roi"

    id: int | None = Field(default=None, primary_key=True)
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

    def get_pixels_from_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Versione alternativa a cui viene passato il frame dall'esterno, in modo da essere più efficiente dentro a un loop.
        """
        (cx, cy), radius = cv2.minEnclosingCircle(self.contours)
        return cv2.getRectSubPix(frame, (int(2 * radius), int(2 * radius)), (cx, cy))

    def get_intensity(self, frame: int) -> float:
        patch = self.get_pixels(frame)

        (cx, cy), radius = cv2.minEnclosingCircle(self.contours)
        x0, y0 = cx - radius, cy - radius

        # Trasla il contorno in coordinate locali della patch
        local_contours = self.contours.copy().astype(np.int32)
        local_contours[:, 0, 0] -= int(x0)
        local_contours[:, 0, 1] -= int(y0)

        mask = np.zeros(patch.shape[:2], np.uint8)
        cv2.drawContours(mask, [local_contours], 0, 255, -1)
        return cv2.mean(patch, mask=mask)

    def get_intensity_from_patch(self, patch: np.ndarray) -> float:
        """
        Versione alternativa a cui viene passato il patch dall'esterno, in modo da essere più efficiente dentro a un loop.
        """
        (cx, cy), radius = cv2.minEnclosingCircle(self.contours)
        x0, y0 = cx - radius, cy - radius

        # Trasla il contorno in coordinate locali della patch
        local_contours = self.contours.copy().astype(np.int32)
        local_contours[:, 0, 0] -= int(x0)
        local_contours[:, 0, 1] -= int(y0)

        mask = np.zeros(patch.shape[:2], np.uint8)
        cv2.drawContours(mask, [local_contours], 0, 255, -1)
        return cv2.mean(patch, mask=mask)
