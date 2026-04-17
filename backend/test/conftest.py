import pytest
from app.services import video_metadata_service


@pytest.fixture
def video_prima():
    return "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/dopo.avi"


@pytest.fixture
def video_dopo():
    return "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/prima.avi"


@pytest.fixture
def total_frames(video_prima, video_dopo):
    return min(
        video_metadata_service.get_video_info(video_prima)["total_frames"],
        video_metadata_service.get_video_info(video_dopo)["total_frames"],
    )
