from fastapi.testclient import TestClient
import pytest
import os
import cv2
import numpy as np

from app.main import app


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
            cv2.imencode(".jpg", cv2.bitwise_and(image, image, mask=mask))[1].tobytes()
        )
