import os
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import video_metadata_service


class TestVideoMetadataService:
    @pytest.fixture(autouse=True)
    def setUp(
        self, pwd, video_prima, video_dopo, brightest_idx_prima, brightest_idx_dopo
    ):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.client = TestClient(app)

        self.pwd = pwd
        self.video_prima = video_prima
        self.video_dopo = video_dopo
        self.brightest_idx_prima = brightest_idx_prima
        self.brightest_idx_dopo = brightest_idx_dopo

    def test_brightest_frame(self):
        """
        Verifica che il frame più luminoso e il suo indice siano quelli corretti.
        """

        brightest_idx, brightest_frame = video_metadata_service.brightest_frame(
            self.video_prima
        )
        assert brightest_idx == self.brightest_idx_prima
        # TODO aggiungere confronto fra immagine estratta e immagine corretta

        out_path = os.path.join(self.pwd, f"out/brightest/prima_{brightest_idx}_.jpeg")
        Image.fromarray(brightest_frame).save(out_path)

        brightest_idx, brightest_frame = video_metadata_service.brightest_frame(
            self.video_dopo
        )
        assert brightest_idx == self.brightest_idx_dopo
        # TODO aggiungere confronto fra immagine estratta e immagine corretta

        out_path = os.path.join(self.pwd, f"out/brightest/dopo_{brightest_idx}_.jpeg")
        Image.fromarray(brightest_frame).save(out_path)
