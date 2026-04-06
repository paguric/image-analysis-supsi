from typing import Annotated

from app.repositories.roi_repo import RoiRepository
from app.db.database import get_session

from fastapi import Depends
from sqlmodel import Session


def get_roi_repository(session: Session = Depends(get_session)) -> RoiRepository:
    return RoiRepository(session)


RoiRepoDep = Annotated[RoiRepository, Depends(get_roi_repository)]
