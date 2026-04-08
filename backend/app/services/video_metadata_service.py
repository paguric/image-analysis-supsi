from app.models.video_metadata import VideoMetadata
from app.repositories.video_metadata_repo import VideoMetadataRepository
from app.models.roi import Analisi


def add_video_metadata(repo: VideoMetadataRepository, metadata: VideoMetadata):
    return repo.add(metadata)


def get_video_metadata(repo: VideoMetadataRepository, fase: Analisi):
    return repo.get(fase)


def list_video_metadata(repo: VideoMetadataRepository):
    return repo.list()
