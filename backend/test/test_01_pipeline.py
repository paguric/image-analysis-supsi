import pytest
import os
import cv2
import numpy as np

import conftest

VIDEO_PRIMA = (
    "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/dopo.avi"
)
VIDEO_DOPO = "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/prima.avi"


def test_db_reset(client):
    response = client.delete("/analysis/reset/")
    assert response.status_code == 200

    # Il db dovrebbe essere vuoto
    response = client.get("/roi/number-of-rois")
    assert response.json() == 0


@pytest.mark.skip(reason="Sostituito con endpoint sotto.")
def test_analysis(client):
    with open(VIDEO_PRIMA, "rb") as f_prima, open(VIDEO_DOPO, "rb") as f_dopo:
        response = client.post(
            "/pipeline/",
            files={
                "video_prima": ("prima.avi", f_prima, "video/x-msvideo"),
                "video_dopo": ("dopo.avi", f_dopo, "video/x-msvideo"),
            },
        )

    assert response.status_code == 200


def test_analysis_local(client):
    response = client.post(
        "/pipeline/local/",
        json={
            "video_prima": VIDEO_PRIMA,
            "video_dopo": VIDEO_DOPO,
        },
    )

    assert response.status_code == 200


# @pytest.mark.skip(reason="")
def test_get_diff(client):
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


def test_get_diff_with_contours(client):
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


def test_get_roi_prima(client):
    """
    Test per estrarre le 20 ROI prima.
    Serve anche a verificare (manualmente) che gli indici corrispondano con quelli del differenziale.
    """
    # Salvataggio su file per check manuale
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/roi", exist_ok=True)
    os.makedirs("out/roi/prima", exist_ok=True)

    for i in range(20):
        response = client.post(
            "/roi/prima/",
            json={
                "index": i,
                "frame": 150,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        # Leggi e salva l'immagine
        image_bytes = response.content

        with open(f"out/roi/prima/idx_{i}_frame_150.jpg", "wb") as f:
            f.write(image_bytes)

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza


def test_get_roi_dopo(client):
    """
    Test per estrarre le 20 ROI dopo.
    Serve anche a verificare (manualmente) che gli indici corrispondano con quelli del differenziale.
    """
    # Salvataggio su file per check manuale
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/roi", exist_ok=True)
    os.makedirs("out/roi/dopo", exist_ok=True)

    for i in range(20):
        response = client.post(
            "/roi/dopo/",
            json={
                "index": i,
                "frame": 150,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

        # Leggi e salva l'immagine
        image_bytes = response.content

        with open(f"out/roi/dopo/idx_{i}_frame_150.jpg", "wb") as f:
            f.write(image_bytes)

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza


def test_get_roi_prima_steps(client):
    # Salvataggio su file per check manuale
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/roi_prima_steps", exist_ok=True)

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

        with open(f"out/roi_prima_steps/roi_10_prima_step_{i}.jpg", "wb") as f:
            f.write(image_bytes)

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza


def test_get_roi_dopo_steps(client):
    # Salvataggio su file per check manuale
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/roi_dopo_steps", exist_ok=True)

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

        with open(f"out/roi_dopo_steps/roi_10_prima_step_{i}.jpg", "wb") as f:
            f.write(image_bytes)

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        assert image is not None
        assert image.shape[0] > 0  # altezza
        assert image.shape[1] > 0  # larghezza


def test_roi_analyzer(client):
    response = client.post(
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
