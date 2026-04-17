import os
import unittest
import pytest
import utils
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import engine
from app.repositories.roi_repo import RoiRepository
from app.services import roi_service
from sqlmodel import Session
from app.schemas.roi import RoiResponse
from app.models.enums import Analisi
from app.dependencies import RoiRepoDep
import cv2
import numpy as np


class RoiControllerTest(unittest.TestCase):
    def setUp(self):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.client = TestClient(app)
        self.session = Session(engine)  # nuova sessione
        self.roi_repo = RoiRepository(self.session)

        os.makedirs("out", exist_ok=True)
        os.makedirs("out/roi", exist_ok=True)
        os.makedirs("out/roi/prima", exist_ok=True)
        os.makedirs("out/roi/dopo", exist_ok=True)

    def tearDown(self):
        self.session.close()

    def test_get_roi_prima(self):
        """
        Verifica /roi/prima/ (estrazione patch ROI).
        """

        for i in range(20):
            response = self.client.post(
                "/roi/prima/",
                json={
                    "index": i,
                    "frame": 150,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            utils.save_image(response.content, f"out/roi/prima/idx_{i}_frame_150.jpg")

    def test_get_roi_dopo(self):
        """
        Verifica /roi/dopo/ (estrazione patch ROI).
        """

        for i in range(20):
            response = self.client.post(
                "/roi/dopo/",
                json={
                    "index": i,
                    "frame": 150,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            utils.save_image(response.content, f"out/roi/dopo/idx_{i}_frame_150.jpg")

    def test_save_new_roi(self):
        """
        Verifica /roi/save/ (sostituzione nuova ROI con vecchia).
        """

        current_roi = self.roi_repo.get(1, Analisi.PRIMA)
        assert current_roi is not None

        new_roi = current_roi.model_copy(deep=True)
        # Si può saltare questo controllo, sicuramente Pydantic non fa errori nella deep copy ma è sempre meglio controllare
        assert current_roi == new_roi

        # Crea un nuovo contorno per simulare l'applicazione della pipeline: il cerchio inscritto all'immagine (che è sempre quadrata)
        patch = new_roi.get_pixels(frame=150)
        h, w = patch.shape[:2]
        center = (w // 2, h // 2)
        radius = min(w, h) // 2
        new_roi.contours = cv2.ellipse2Poly(center, (radius, radius), 0, 0, 360, 1)

        assert current_roi != new_roi

        response = self.client.post("/roi/save/", roi_service.roi_to_response(new_roi))
        assert response.status_code == 200

        # TODO verificare che ci sia una sola ROI per quell'indice per quella analisi nel db, che non ci siano id duplicati, che la ROI "vecchia" non sia più nel db e che quella nuova invece sì

    def test_intensity_extraction(self):
        """
        Verifica il funzionamento di cv2.drawContours(mask, [contours], 0, 255, -1).
        """

        response = self.client.post(
            "/roi/prima/",
            json={
                "index": 15,
                "frame": 150,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        # Legge l'immagine
        image_bytes = response.content

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza

        # Crea un contorno "falso": il cerchio inscritto all'immagine (che è sempre quadrata)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        radius = min(w, h) // 2
        contours = cv2.ellipse2Poly(center, (radius, radius), 0, 0, 360, 1)

        mask = np.zeros(image.shape[:2], np.uint8)
        cv2.drawContours(mask, [contours], 0, 255, -1)

        print("MEAN TEST")
        print(cv2.mean(image, mask=mask))

        # Salvataggio su file per check manuale
        os.makedirs("out", exist_ok=True)
        os.makedirs("out/intensity", exist_ok=True)

        with open("out/intensity/intensity_with_mask.jpg", "wb") as f:
            f.write(
                cv2.imencode(".jpg", cv2.bitwise_and(image, image, mask=mask))[
                    1
                ].tobytes()
            )
