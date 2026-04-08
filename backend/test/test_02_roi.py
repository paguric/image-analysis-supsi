from fastapi.testclient import TestClient
import pytest
import os
import cv2
import numpy as np

from app.main import app


@pytest.mark.skip(reason="Mi sono accorto a metà che non serve a niente, per ora")
def test_intensity_extraction(client):
    """
    Testa che questa funzione cv2.drawContours(mask, [contours], 0, 255, -1) faccia effettivamente il suo lavoro
    """

    response = client.post(
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
    # TODO
    contours = None

    mask = np.zeros(image, np.uint8)
    cv2.drawContours(mask, [contours], 0, 255, -1)
