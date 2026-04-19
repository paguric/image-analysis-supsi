import os
import pytest
from app.services import video_metadata_service


@pytest.fixture
def pwd():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def video_prima(pwd):
    return os.path.join(pwd, "prima.avi")


@pytest.fixture
def video_dopo(pwd):
    return os.path.join(pwd, "dopo.avi")


@pytest.fixture
def total_frames(video_prima, video_dopo):
    return min(
        video_metadata_service.get_video_info(video_prima)["total_frames"],
        video_metadata_service.get_video_info(video_dopo)["total_frames"],
    )
