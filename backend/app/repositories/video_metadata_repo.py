from app.models.video_metadata import VideoMetadata
from app.models.enums import Analisi


class VideoMetadataRepository:
    def __init__(self, session):
        self.session = session

    def add(self, metadata):
        self.session.add(metadata)
        self.session.commit()
        self.session.refresh(metadata)

    def get(self, fase: Analisi):
        return self.session.query(VideoMetadata).filter_by(fase=fase).one()

    def list(self):
        return self.session.query(VideoMetadata).all()
