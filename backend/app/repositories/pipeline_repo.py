class PipelineRepository:
    def __init__(self, session):
        self.session = session

    def add(self, pipeline):
        self.session.add(pipeline)
        self.session.commit()
        self.session.refresh(pipeline)

    """def get(self, idx: int, fase: Analisi):
        return self.session.query(Roi).filter_by(idx=idx).filter_by(fase=fase).one()

    def list(self, fase: Analisi):
        return self.session.query(Roi).filter_by(fase=fase).all()"""
