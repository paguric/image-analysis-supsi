import cv2
import numpy as np


def save_image(image_bytes: bytes, out_path: str):

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    assert image is not None
    assert image.shape[0] > 0  # altezza
    assert image.shape[1] > 0  # larghezza

    # Salva l'immagine
    with open(out_path, "wb") as f:
        f.write(image_bytes)


def sanity_check(client, idx: int, frame: int, file_name: str):
    response = client.post(
        "/roi/prima/",
        json={"index": idx, "frame": frame},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    save_image(
        response.content,
        f"out/roi/prima/{file_name}",
    )
