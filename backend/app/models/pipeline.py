import io
import numpy as np
from typing import Optional

from sqlmodel import Field, SQLModel, Column, Relationship
from pydantic import ConfigDict
from sqlalchemy import LargeBinary


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipeline"

    id: int | None = Field(default=None, primary_key=True)
    roi_id: int | None = Field(default=None, foreign_key="roi.id")
    roi: Optional["Roi"] = Relationship(back_populates="pipelines")

    hpf_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))
    enhanced_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))
    edges_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))
    edges_closed_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

    # Abilitazione tipi arbitrari calcolati on-demand
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def hpf(self) -> np.ndarray | None:
        if self.hpf_data is None:
            return None
        buffer = io.BytesIO(self.hpf_data)
        return np.load(buffer, allow_pickle=False)

    @hpf.setter
    def hpf(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.hpf_data = buffer.getvalue()

    @property
    def enhanced(self) -> np.ndarray | None:
        if self.enhanced_data is None:
            return None
        buffer = io.BytesIO(self.enhanced_data)
        return np.load(buffer, allow_pickle=False)

    @enhanced.setter
    def enhanced(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.enhanced_data = buffer.getvalue()

    @property
    def edges(self) -> np.ndarray | None:
        if self.edges_data is None:
            return None
        buffer = io.BytesIO(self.edges_data)
        return np.load(buffer, allow_pickle=False)

    @edges.setter
    def edges(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.edges_data = buffer.getvalue()

    @property
    def edges_closed(self) -> np.ndarray | None:
        if self.edges_closed_data is None:
            return None
        buffer = io.BytesIO(self.edges_closed_data)
        return np.load(buffer, allow_pickle=False)

    @edges_closed.setter
    def edges_closed(self, value: np.ndarray):
        buffer = io.BytesIO()
        np.save(buffer, value)
        self.edges_closed_data = buffer.getvalue()
