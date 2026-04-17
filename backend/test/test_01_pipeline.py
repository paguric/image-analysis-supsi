import os
import cv2
import unittest
import pytest
import utils
from fastapi.testclient import TestClient
from app.main import app
from pydantic_core import from_json
from app.schemas.roi import RoiResponse
from app.services import video_metadata_service


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

        # Non capisco perchè, ma se genero una clip non trova più un paio di ROI
        return

        # Crea una copia tagliata del video, in modo che i test eseguano più velocemente
        self.total_frames = 260

        # Estrae una clip di lunghezza (in frame) self.total_frames attorno al frame più luminoso del video dopo
        # Per non dover eseguire video_metadata_service.brightest_frame sul video prima (non avrebbe più senso il taglio a quel punto),
        # Imposto manualmente il frame più luminoso

        # print(video_metadata_service.brightest_frame(self.video_dopo))
        # print(video_metadata_service.brightest_frame(self.video_prima)) -> 165
        self.brightest_idx = 161

        os.makedirs("./test", exist_ok=True)
        self.video_prima_clip = "./test/prima_clip.avi"
        self.video_dopo_clip = "./test/dopo_clip.avi"

        if os.path.exists(self.video_prima_clip) and os.path.exists(
            self.video_dopo_clip
        ):
            return

        half = self.total_frames // 2
        start = self.brightest_idx - half

        def _cut(src, dst):
            cap = cv2.VideoCapture(src)
            fps = cap.get(cv2.CAP_PROP_FPS)
            w, h = (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            )
            out = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"XVID"), fps, (w, h))
            cap.set(cv2.CAP_PROP_POS_FRAMES, start)
            for _ in range(self.total_frames):
                ret, frame = cap.read()
                out.write(frame)
            cap.release()
            out.release()

        _cut(self.video_dopo, self.video_dopo_clip)
        _cut(self.video_prima, self.video_prima_clip)

    def tearDown(self):
        return None

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
                    "frame": self.total_frames // 2,
                },
            )

            assert response.status_code == 200, (
                f"ROI {i} analisi prima mancante nel db."
            )

        for i in range(20):
            response = self.client.post(
                "/roi/dopo/",
                json={
                    "index": i,
                    "frame": self.total_frames // 2,
                },
            )

            assert response.status_code == 200, f"ROI {i} analisi dopo mancante nel db."

    def test_get_diff(self):
        """
        Verifica /pipeline/diff/{frame}/ (differenziale globale).
        """
        response = self.client.get(f"/pipeline/diff/{self.total_frames // 2}/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        utils.save_image(
            response.content, f"out/diff/diff_frame_{self.total_frames // 2}.jpg"
        )

    def test_get_diff_with_contours(self):
        """
        Verifica /pipeline/diff/{frame}/contours/ (differenziale globale con contorni).
        """
        response = self.client.get(f"/pipeline/diff/{self.total_frames // 2}/contours/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        utils.save_image(
            response.content,
            f"out/diff/diff_frame_{self.total_frames // 2}_contours.jpg",
        )

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

            utils.save_image(
                response.content, f"out/roi/prima/steps/roi_10_prima_step_{i}.jpg"
            )

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

            utils.save_image(
                response.content, f"out/roi/dopo/steps/roi_10_prima_step_{i}.jpg"
            )

    def test_roi_analyzer(self):
        """
        Verifica /pipeline/roi/prima/{idx}/ (creazione BaseModel RoiResponse).
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

        roi = RoiResponse.model_validate(response.json())
        assert roi.idx != 0
        assert roi.video_path != ""
        assert roi.fase != None
        assert roi.contours != None
