import os
import pytest
import utils
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import engine
from app.repositories.roi_repo import RoiRepository
from app.services import roi_service
from app.services import video_metadata_service
from sqlmodel import Session
from app.schemas.roi import RoiResponse
from app.models.enums import Analisi
from app.models.roi import Roi
from app.dependencies import RoiRepoDep
from app.dependencies import get_session
import cv2
import numpy as np


class TestRoiController:
    @pytest.fixture(autouse=True)
    def setup(self, video_prima, video_dopo, total_frames):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.session = Session(engine)
        self.roi_repo = RoiRepository(self.session)

        def override_get_session():
            yield self.session

        app.dependency_overrides[get_session] = override_get_session
        self.client = TestClient(app)

        self.video_prima = video_prima
        self.video_dopo = video_dopo
        self.total_frames = total_frames

        os.makedirs("out", exist_ok=True)
        os.makedirs("out/roi", exist_ok=True)
        os.makedirs("out/roi/prima", exist_ok=True)
        os.makedirs("out/roi/dopo", exist_ok=True)

        yield  # esegue i test (equivale al tearDown di unittest)

        app.dependency_overrides.clear()
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
                    "frame": self.total_frames // 2,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            utils.save_image(
                response.content,
                f"out/roi/prima/idx_{i}_frame_{self.total_frames // 2}.jpg",
            )

    def test_get_roi_dopo(self):
        """
        Verifica /roi/dopo/ (estrazione patch ROI).
        """

        for i in range(20):
            response = self.client.post(
                "/roi/dopo/",
                json={
                    "index": i,
                    "frame": self.total_frames // 2,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            utils.save_image(
                response.content,
                f"out/roi/dopo/idx_{i}_frame_{self.total_frames // 2}.jpg",
            )

    # @pytest.mark.skip(reason="Da rifare, sia il test che l'endpoint.")
    def test_save_new_roi(self):
        """
        Verifica /roi/save/ (sostituzione contorni di una ROI).
        """

        i = 0
        current_roi = self.roi_repo.get(i, Analisi.PRIMA)
        assert current_roi is not None

        new_roi = Roi.model_validate(current_roi.model_dump())

        # Crea un nuovo contorno per simulare l'applicazione della pipeline: il cerchio inscritto all'immagine (che è sempre quadrata)
        cx, cy = new_roi.get_center()
        h, w = new_roi.get_pixels(self.total_frames // 2).shape[:2]
        radius = min(w, h) // 2
        angles = np.linspace(0, 2 * np.pi, 360, endpoint=False)
        pts = np.stack(
            [cx + radius * np.cos(angles), cy + radius * np.sin(angles)], axis=1
        ).astype(np.int32)
        new_roi.contours = pts[:, np.newaxis, :]

        response = self.client.post(
            "/roi/save/",
            json=roi_service.roi_to_response(new_roi).model_dump(mode="json"),
        )
        assert response.status_code == 200

        # Check manuale: salva la patch con contorni di self.roi_repo.get(i, Analisi.PRIMA) per verificare se il contorno nel backend è cambiato
        response = self.client.post(
            "/roi/prima/",
            json={
                "index": i,
                "frame": self.total_frames // 2,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        utils.save_image(
            response.content,
            f"out/roi/prima/idx_{i}_frame_{self.total_frames // 2}_aftersave.jpg",
        )

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
