from typing import Annotated

from app.repositories.roi_repo import RoiRepository
from app.repositories.pipeline_repo import PipelineRepository
from app.repositories.video_metadata_repo import VideoMetadataRepository
from app.db.database import get_session

from fastapi import Depends
from sqlmodel import Session


def get_roi_repository(session: Session = Depends(get_session)) -> RoiRepository:
    return RoiRepository(session)


def get_pipeline_repository(
    session: Session = Depends(get_session),
) -> PipelineRepository:
    return PipelineRepository(session)


def get_video_metadata_repository(
    session: Session = Depends(get_session),
) -> VideoMetadataRepository:
    return VideoMetadataRepository(session)


RoiRepoDep = Annotated[RoiRepository, Depends(get_roi_repository)]

PipelineRepoDep = Annotated[PipelineRepository, Depends(get_pipeline_repository)]

VideoMetadataRepoDep = Annotated[
    VideoMetadataRepository, Depends(get_video_metadata_repository)
]
