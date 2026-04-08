from fastapi.testclient import TestClient
import pytest
import os
import cv2
import numpy as np

from app.routers import roi_controller

from app.main import app

client = TestClient(app)

VIDEO_PRIMA = "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/prima.avi"
VIDEO_DOPO = (
    "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/dopo.avi"
)


def test_db_reset():
    response = client.delete("/analysis/reset/")
    assert response.status_code == 200

    # Il db dovrebbe essere vuoto
    response = client.get("/roi/number-of-rois")
    assert response.json() == 0


# @pytest.mark.skip(reason="")
def test_analysis():
    with open(VIDEO_PRIMA, "rb") as f_prima, open(VIDEO_DOPO, "rb") as f_dopo:
        response = client.post(
            "/pipeline/",
            files={
                "video_prima": ("prima.avi", f_prima, "video/x-msvideo"),
                "video_dopo": ("dopo.avi", f_dopo, "video/x-msvideo"),
            },
        )

    assert response.status_code == 200


# @pytest.mark.skip(reason="")
def test_get_diff():
    response = client.get("/pipeline/diff/100/")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    # Leggi e salva l'immagine
    image_bytes = response.content

    # Salvataggio su file per check manuale
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/diff", exist_ok=True)

    with open("out/diff/diff_frame_100.jpg", "wb") as f:
        f.write(image_bytes)

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    assert image is not None
    assert image.shape[0] > 0  # altezza
    assert image.shape[1] > 0  # larghezza


def test_get_diff_with_contours():
    response = client.get("/pipeline/diff/100/contours/")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    # Leggi e salva l'immagine
    image_bytes = response.content

    # Salvataggio su file per check manuale
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/diff", exist_ok=True)

    with open("out/diff/diff_frame_100_contours.jpg", "wb") as f:
        f.write(image_bytes)

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    assert image is not None
    assert image.shape[0] > 0  # altezza
    assert image.shape[1] > 0  # larghezza


def test_get_roi_prima_steps():
    for i in range(4):
        response = client.post(
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

        # Leggi e salva l'immagine
        image_bytes = response.content

        # Salvataggio su file per check manuale
        os.makedirs("out", exist_ok=True)
        os.makedirs("out/roi_prima_steps/", exist_ok=True)

        with open(f"out/roi_prima_steps/roi_10_prima_step_{i}.jpg", "wb") as f:
            f.write(image_bytes)

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza


def test_get_roi_dopo_steps():
    for i in range(4):
        response = client.post(
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

        # Leggi e salva l'immagine
        image_bytes = response.content

        # Salvataggio su file per check manuale
        os.makedirs("out", exist_ok=True)
        os.makedirs("out/roi_dopo_steps/", exist_ok=True)

        with open(f"out/roi_dopo_steps/roi_10_prima_step_{i}.jpg", "wb") as f:
            f.write(image_bytes)

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza
