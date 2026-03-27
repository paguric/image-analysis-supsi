import cv2
import numpy as np
from app.helpers import cv2_utils


class Roi:
    def __init__(self, video_path: str, idx: int):
        self.video_path = video_path
        self.idx = idx

    def set_contours(self, contours: np.ndarray):
        self.contours = contours

    def get_center(self) -> tuple[int, int]:
        (cx, cy), _ = cv2.minEnclosingCircle(self.contours)
        return (int(cx), int(cy))

    def get_pixels(self, frame: int) -> np.ndarray:
        """
        Estrae il patch dal frame del video specificato.
        Per patch si intende la matrice quadrata (width = height) dove si trova il min enclosing circle.
        """
        img = cv2_utils.extract_frame(self.video_path, frame)
        (cx, cy), radius = cv2.minEnclosingCircle(self.contours)
        return cv2.getRectSubPix(img, (int(2 * radius), int(2 * radius)), (cx, cy))
