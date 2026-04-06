import io
import numpy as np
from typing import Optional

from app.schemas.pipeline_params import PipelineParams

from sqlmodel import Field, SQLModel, Column, Relationship
from pydantic import ConfigDict
from sqlalchemy import LargeBinary, JSON


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipeline"

    id: int | None = Field(default=None, primary_key=True)
    roi_id: int | None = Field(default=None, foreign_key="roi.id")
    roi: Optional["Roi"] = Relationship(back_populates="pipelines")

    params_data: dict | None = Field(default=None, sa_column=Column(JSON))
    hpf_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))
    enhanced_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))
    edges_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))
    edges_closed_data: bytes | None = Field(default=None, sa_column=Column(LargeBinary))

    # Abilitazione tipi arbitrari calcolati on-demand
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_steps(
        cls, roi_id: int, steps: list[np.ndarray], params: PipelineParams
    ) -> "Pipeline":
        pipeline = cls(roi_id=roi_id)
        pipeline.params = params
        pipeline.hpf = steps[0]
        pipeline.enhanced = steps[1]
        pipeline.edges = steps[2]
        pipeline.edges_closed = steps[3]
        return pipeline

    @property
    def params(self) -> PipelineParams:
        return PipelineParams(**(self.params_data or {}))

    @params.setter
    def params(self, value: PipelineParams):
        self.params_data = value.model_dump()

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

    def get_step(self, i: int) -> np.ndarray:
        match i:
            case 0:
                return self.hpf
            case 1:
                return self.enhanced
            case 2:
                return self.edges
            case 3:
                return self.edges_closed
