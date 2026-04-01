import io
import numpy as np

from app.models.roi import Analisi

from sqlmodel import Field, SQLModel, Column, Enum as SAEnum
from pydantic import ConfigDict
from sqlalchemy import LargeBinary


class VideoMetadata(SQLModel, table=True):
    __tablename__ = "video"

    id: int | None = Field(default=None, primary_key=True)
    video_path: str
    fase: Analisi = Field(default=None, sa_column=Column(SAEnum(Analisi)))
    brightest_idx: int

    # Colonna binaria grezza sul DB
    brightest_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

    # Abilitazione tipi arbitrari calcolati on-demand
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def brightest_frame(self) -> np.ndarray | None:
        if self.brightest_data is None:
            return None
        buffer = io.BytesIO(self.brightest_data)
        return np.load(buffer, allow_pickle=False)

    @brightest_frame.setter
    def brightest_frame(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.brightest_data = buffer.getvalue()
