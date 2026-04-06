from app.models.pipeline import Pipeline
from app.schemas.pipeline_params import PipelineParams


class PipelineRepository:
    def __init__(self, session):
        self.session = session

    def add(self, pipeline):
        self.session.add(pipeline)
        self.session.commit()
        self.session.refresh(pipeline)

    def get(self, roi_id: int, params: PipelineParams):
        return (
            self.session.query(Pipeline)
            .filter_by(roi_id=roi_id)
            .filter_by(params=params)
            .one()
        )
