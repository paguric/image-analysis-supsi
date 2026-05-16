import os
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAnalysisController:
    @pytest.fixture(autouse=True)
    def setUp(self, video_prima, video_dopo, total_frames, min_freq, max_freq):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.client = TestClient(app)

        self.video_prima = video_prima
        self.video_dopo = video_dopo
        self.total_frames = total_frames
        self.min_freq = min_freq
        self.max_freq = max_freq

    def test_csv(self):
        """
        Verifica /analysis/diff/results/{min_freq}/{max_freq}/ (calcolo CSV globale).
        """
        # analysis_service.compute_diff_csv legge il path dei video dalla prima ROI per le due analisi
        # Per eseguire più rapidamente, modifica temporaneamente il path delle prime due ROI in modo da puntare ad una clip più breve
        # TODO

        response = self.client.get(
            f"/analysis/diff/results/{self.min_freq}/{self.max_freq}/"
        )
        assert response.status_code == 200

        if response.json()["success"]:
            assert os.path.exists(response.json()["path"])

        # TODO Ripristina il path originale per le due ROI modificate

    def test_csv_pixels(self):
        """
        Verifica /analysis/export-csv/diff/frame/{frame}/pixels/ (calcolo CSV pixel-pixel).
        """
        response = self.client.get(
            f"/analysis/export-csv/diff/frame/{self.total_frames // 2}/pixels/"
        )
        assert response.status_code == 200

        if response.json()["success"]:
            assert os.path.exists(response.json()["path"])
