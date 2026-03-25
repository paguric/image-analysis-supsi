import numpy as np

class ROI:

    def __init__(self, video_path: str, idx: int):
        self.video_path = video_path
        self.idx = idx

    def set_center(self, center: tuple[int, int]):
        self.center = center

    def set_contours(self, contours: np.ndarray):
        self.contours = contours