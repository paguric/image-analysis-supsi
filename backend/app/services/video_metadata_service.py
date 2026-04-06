from app.repositories.video_metadata_repo import VideoMetadataRepository
from app.models.roi import Analisi


def get_video_metadata(repo: VideoMetadataRepository, fase: Analisi):
    return repo.get(fase)
