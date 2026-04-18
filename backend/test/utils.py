import cv2
import numpy as np
from app.models.roi import Roi


def save_image(image_bytes: bytes, out_path: str):

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    assert image is not None
    assert image.shape[0] > 0  # altezza
    assert image.shape[1] > 0  # larghezza

    # Salva l'immagine
    with open(out_path, "wb") as f:
        f.write(image_bytes)


def apply_special_contours(roi: Roi):
    """
    Modifica i contorni della ROI trasformandoli in una stella.
    """
    cx, cy = roi.get_center()
    h, w = roi.get_pixels(1).shape[:2]
    radius = min(w, h) // 2
    n = 5
    outer, inner = radius, radius // 2
    angles = np.linspace(0, 2 * np.pi, n * 2, endpoint=False)
    angles[1::2] += np.pi / n
    r = np.where(np.arange(n * 2) % 2 == 0, outer, inner)
    pts = np.stack([cx + r * np.cos(angles), cy + r * np.sin(angles)], axis=1).astype(
        np.int32
    )
    roi.contours = pts[:, np.newaxis, :]
