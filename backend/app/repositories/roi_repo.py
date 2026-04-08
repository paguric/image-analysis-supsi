from app.models.roi import Roi
from app.models.roi import Analisi


class RoiRepository:
    def __init__(self, session):
        self.session = session

    def add(self, roi):
        self.session.add(roi)
        self.session.commit()
        self.session.refresh(roi)

    def get(self, idx: int, fase: Analisi):
        return self.session.query(Roi).filter_by(idx=idx).filter_by(fase=fase).one()

    def list_all(self):
        return self.session.query(Roi).all()

    def list(self, fase: Analisi):
        return self.session.query(Roi).filter_by(fase=fase).all()
