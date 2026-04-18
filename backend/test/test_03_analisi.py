import os
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAnalysisController:
    @pytest.fixture(autouse=True)
    def setUp(self, video_prima, video_dopo, total_frames):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.client = TestClient(app)

        self.video_prima = video_prima
        self.video_dopo = video_dopo
        self.total_frames = total_frames

    @pytest.mark.skip(reason="")
    def test_csv(self):
        """
        Verifica /analysis/diff/results/{min_freq}/{max_freq}/ (calcolo CSV globale).
        """
        response = self.client.get("/analysis/diff/results/420/730/")
        assert response.status_code == 200

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
            print("DEBUG")
