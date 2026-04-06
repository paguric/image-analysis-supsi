from app.models.roi import Roi
from app.models.roi import Analisi


class RoiRepository:
    def __init__(self, session):
        self.session = session

    def add(self, metadata):
        self.session.add(metadata)

    def get(self, idx: int, fase: Analisi):
        return self.session.query(Roi).filter_by(idx=idx).filter_by(fase=fase).one()

    def list(self, fase: Analisi):
        return self.session.query(Roi).filter_by(fase=fase).all()
