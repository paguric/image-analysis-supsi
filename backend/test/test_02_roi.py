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
    def setup(self, pwd, video_prima, video_dopo, total_frames):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.session = Session(engine)
        self.roi_repo = RoiRepository(self.session)

        def override_get_session():
            yield self.session

        app.dependency_overrides[get_session] = override_get_session
        self.client = TestClient(app)

        self.pwd = pwd
        self.video_prima = video_prima
        self.video_dopo = video_dopo
        self.total_frames = total_frames

        base = os.path.join(pwd, "out")

        folders = [
            "",
            "roi",
            "roi/prima",
            "roi/dopo",
        ]

        for folder in folders:
            os.makedirs(os.path.join(base, folder), exist_ok=True)

        yield  # esegue i test (equivale al tearDown di unittest)

        app.dependency_overrides.clear()
        self.session.close()

    def test_get_roi_prima(self):
        """
        Verifica /roi/prima/ (estrazione patch ROI).
        """

        for i in range(20):
            # Test senza overlap
            response = self.client.post(
                "/roi/prima/",
                json={
                    "data": {
                        "index": i,
                        "frame": self.total_frames // 2,
                    },
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            out_path = os.path.join(
                self.pwd, f"out/roi/prima/idx_{i}_frame_{self.total_frames // 2}.jpg"
            )
            utils.save_image(response.content, out_path)

            # Test con overlap di un'altra ROI
            roi_clone = Roi.model_validate(
                self.roi_repo.get(i, Analisi.PRIMA).model_dump()
            )
            utils.apply_special_contours(roi_clone)
            roi_clone_response = roi_service.roi_to_response(roi_clone)

            response = self.client.post(
                "/roi/prima/",
                json={
                    "data": {
                        "index": i,
                        "frame": self.total_frames // 2,
                    },
                    "response": roi_clone_response.model_dump(),
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            out_path = os.path.join(
                self.pwd,
                f"out/roi/prima/idx_{i}_frame_{self.total_frames // 2}_with_overlap.jpg",
            )
            utils.save_image(response.content, out_path)

    def test_get_roi_dopo(self):
        """
        Verifica /roi/dopo/ (estrazione patch ROI).
        """

        for i in range(20):
            response = self.client.post(
                "/roi/dopo/",
                json={
                    "data": {
                        "index": i,
                        "frame": self.total_frames // 2,
                    },
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            out_path = os.path.join(
                self.pwd, f"out/roi/dopo/idx_{i}_frame_{self.total_frames // 2}.jpg"
            )
            utils.save_image(response.content, out_path)

            # Test con overlap di un'altra ROI
            roi_clone = Roi.model_validate(
                self.roi_repo.get(i, Analisi.PRIMA).model_dump()
            )
            utils.apply_special_contours(roi_clone)
            roi_clone_response = roi_service.roi_to_response(roi_clone)

            response = self.client.post(
                "/roi/dopo/",
                json={
                    "data": {
                        "index": i,
                        "frame": self.total_frames // 2,
                    },
                    "response": roi_clone_response.model_dump(),
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpeg"

            out_path = os.path.join(
                self.pwd,
                f"out/roi/dopo/idx_{i}_frame_{self.total_frames // 2}_with_overlap.jpg",
            )
            utils.save_image(response.content, out_path)

    def test_save_new_roi(self):
        """
        Verifica /roi/save/ (sostituzione contorni di una ROI).
        """

        i = 0
        current_roi = self.roi_repo.get(i, Analisi.PRIMA)
        assert current_roi is not None

        new_roi = Roi.model_validate(current_roi.model_dump())

        # Crea un nuovo contorno per simulare l'applicazione della pipeline: una sorta di stella (in modo sia visibile facilmente)
        utils.apply_special_contours(new_roi)

        response = self.client.post(
            "/roi/save/",
            json=roi_service.roi_to_response(new_roi).model_dump(mode="json"),
        )
        assert response.status_code == 200

        # Check manuale: salva la patch con contorni di self.roi_repo.get(i, Analisi.PRIMA) per verificare se il contorno nel backend è cambiato
        response = self.client.post(
            "/roi/prima/",
            json={
                "data": {
                    "index": i,
                    "frame": self.total_frames // 2,
                },
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        out_path = os.path.join(
            self.pwd,
            f"out/roi/prima/idx_{i}_frame_{self.total_frames // 2}_aftersave.jpg",
        )
        utils.save_image(response.content, out_path)

        # Cleanup: re-inserisce la ROI originale nel db
        self.client.post(
            "/roi/save/",
            json=roi_service.roi_to_response(current_roi).model_dump(mode="json"),
        )

    @pytest.mark.skip(reason="Da spostare/refactorare.")
    def test_intensity_extraction(self):
        """
        Verifica il funzionamento di cv2.drawContours(mask, [contours], 0, 255, -1).
        """

        i = 0
        response = self.client.post(
            "/roi/prima/",
            json={
                "data": {
                    "index": i,
                    "frame": self.total_frames // 2,
                },
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

        """# Salvataggio su file per check manuale
        os.makedirs("out", exist_ok=True)
        os.makedirs("out/intensity", exist_ok=True)

        with open("out/intensity/intensity_with_mask.jpg", "wb") as f:
            f.write(
                cv2.imencode(".jpg", cv2.bitwise_and(image, image, mask=mask))[
                    1
                ].tobytes()
            )"""
