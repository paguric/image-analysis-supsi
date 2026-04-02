import io
import numpy as np
from typing import Optional

from sqlmodel import Field, SQLModel, Column, Relationship
from pydantic import ConfigDict
from sqlalchemy import LargeBinary


class Diff(SQLModel, table=True):
    __tablename__ = "diff"

    id: int | None = Field(default=None, primary_key=True)
    roi_id: int | None = Field(default=None, foreign_key="roi.id")
    roi: Optional["Roi"] = Relationship(back_populates="pipelines")

    frame_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

    # Abilitazione tipi arbitrari calcolati on-demand
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def frame(self) -> np.ndarray | None:
        if self.frame_data is None:
            return None
        buffer = io.BytesIO(self.frame_data)
        return np.load(buffer, allow_pickle=False)

    @frame.setter
    def frame(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.frame_data = buffer.getvalue()
