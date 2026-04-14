import unittest
import pytest
from fastapi.testclient import TestClient
from app.main import app

import os
import cv2
import numpy as np


class PipelineControllerTest(unittest.TestCase):
    def setUp(self):
        """
        Inizializza il client di test, imposta il percorso dei video da analizzare e crea le cartelle dove salvare
        i file di output per ogni test.
        """
        self.client = TestClient(app)
        self.video_prima = "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/dopo.avi"
        self.video_dopo = "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/prima.avi"
        
        os.makedirs("out", exist_ok=True)
        os.makedirs("out/diff", exist_ok=True)
        os.makedirs("out/roi", exist_ok=True)
        os.makedirs("out/roi/prima", exist_ok=True)
        os.makedirs("out/roi/dopo", exist_ok=True)
        os.makedirs("out/roi/prima/steps", exist_ok=True)
        os.makedirs("out/roi/dopo/steps", exist_ok=True)


    def tearDown(self):  
        return None
    

    def save_image(self, image_bytes: bytes, out_path: str):

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza

        # Salva l'immagine
        with open(out_path, "wb") as f:
            f.write(image_bytes)


    @pytest.mark.order(1)
    def test_db_reset(self):
        """
        Verifica /analysis/reset/ (reset del db).
        """
        response = self.client.delete("/analysis/reset/")
        assert response.status_code == 200

        # Il db dovrebbe essere vuoto
        response = self.client.get("/roi/number-of-rois")
        assert response.json() == 0
    

    def test_analysis_local(self):
        """
        Verifica /pipeline/local/ (analisi con lettura dei video da disco, senza upload di file).
        """
        response = self.client.post(
            "/pipeline/local/",
            json={
                "video_prima": self.video_prima,
                "video_dopo": self.video_dopo,
            },
        )

        assert response.status_code == 200

        # Sotto-test per verificare ci siano tutte e 40 le ROI nel db.
        for i in range(20):
            response = self.client.post(
                "/roi/prima/",
                json={
                    "index": i,
                    "frame": 150,
                },
            )

            assert response.status_code == 200, f"ROI {i} analisi prima mancante nel db."


        for i in range(20):
            response = self.client.post(
                "/roi/dopo/",
                json={
                    "index": i,
                    "frame": 150,
                },
            )

            assert response.status_code == 200, f"ROI {i} analisi dopo mancante nel db."


    def test_get_diff(self):
        """
        Verifica /pipeline/diff/{frame}/ (differenziale globale).
        """
        response = self.client.get("/pipeline/diff/100/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        self.save_image(response.content, "out/diff/diff_frame_100.jpg")
    

    def test_get_diff_with_contours(self):
        """
        Verifica /pipeline/diff/{frame}/contours/ (differenziale globale con contorni).
        """
        response = self.client.get("/pipeline/diff/100/contours/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        self.save_image(response.content, "out/diff/diff_frame_100_contours.jpg")


    def test_get_roi_prima_steps(self):
        """
        Verifica /pipeline/roi/prima/{idx}/step/{i}/ (applicazione della pipeline su una singola ROI).
        """
        for i in range(4):
            response = self.client.post(
                f"/pipeline/roi/prima/10/step/{i}/",
                json={
                    "bg_blur_size": 101,
                    "canny_low": 0,
                    "canny_high": 0,
                    "clahe_clip_limit": 3.0,
                    "clahe_grid_size": 8,
                    "morph_kernel_size": 3,
                    "morph_iterations": 4,
                    "min_area": 5000,
                    "min_circularity": 0.10,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            self.save_image(response.content, f"out/roi/prima/steps/roi_10_prima_step_{i}.jpg")


    def test_get_roi_dopo_steps(self):
        """
        Verifica /pipeline/roi/dopo/{idx}/step/{i}/ (applicazione della pipeline su una singola ROI).
        """

        for i in range(4):
            response = self.client.post(
                f"/pipeline/roi/dopo/10/step/{i}/",
                json={
                    "bg_blur_size": 101,
                    "canny_low": 0,
                    "canny_high": 0,
                    "clahe_clip_limit": 3.0,
                    "clahe_grid_size": 8,
                    "morph_kernel_size": 3,
                    "morph_iterations": 4,
                    "min_area": 5000,
                    "min_circularity": 0.10,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            self.save_image(response.content, f"out/roi/dopo/steps/roi_10_prima_step_{i}.jpg")


    def test_roi_analyzer(self):
        """
        Verifica /pipeline/roi/prima/1/ (creazione BaseModel RoiResponse)
        """
        
        response = self.client.post(
            "/pipeline/roi/prima/1/",
            json={
                "bg_blur_size": 101,
                "canny_low": 0,
                "canny_high": 0,
                "clahe_clip_limit": 3.0,
                "clahe_grid_size": 8,
                "morph_kernel_size": 3,
                "morph_iterations": 4,
                "min_area": 5000,
                "min_circularity": 0.10,
            },
        )

        assert response.status_code == 200
