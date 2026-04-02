import io
import numpy as np

from sqlmodel import Field, SQLModel, Column
from pydantic import ConfigDict
from sqlalchemy import LargeBinary


class Diff(SQLModel, table=True):
    __tablename__ = "diff"

    id: int | None = Field(default=None, primary_key=True)
    frame: int

    diff_frame_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

    # Abilitazione tipi arbitrari calcolati on-demand
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def diff_frame(self) -> np.ndarray | None:
        if self.diff_frame_data is None:
            return None
        buffer = io.BytesIO(self.diff_frame_data)
        return np.load(buffer, allow_pickle=False)

    @diff_frame.setter
    def diff_frame(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.diff_frame_data = buffer.getvalue()
