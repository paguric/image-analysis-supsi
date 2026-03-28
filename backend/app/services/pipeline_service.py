import cv2
import numpy as np

from app.services import cv2_service
from app.models.roi import Roi
from app.schemas.roi import RoiData
from app.services import roi_service
from app.services import normalization_service

PARAMS = {
    "bg_blur_size": 101,
    "canny_low": 0,
    "canny_high": 0,
    "bilateral_d": 5,
    "bilateral_sigma_color": 50,
    "bilateral_sigma_space": 1,
    "morph_kernel_size": 3,
    "morph_iterations": 2,
    "min_area": 5000,
    "min_circularity": 0.10,
}


def ensure_odd(v: int) -> int:
    """OpenCV richiede kernel di dimensione dispari."""
    v = max(1, int(v))
    return v if v % 2 == 1 else v + 1


def contour_circularity(contour: np.ndarray) -> float:
    """Quanto il contorno assomiglia a un cerchio (1.0 = cerchio perfetto)."""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, closed=True)
    if perimeter < 1e-6:
        return 0
    return 4 * np.pi * area / (perimeter**2)


# -------------------------------------


def pipeline(img: np.ndarray) -> np.ndarray | None:
    """
    HPF → CLAHE → Canny → closing
    restituisce l'immgaine binaria da cui estrarre i contorni
    """
    bg_blur = ensure_odd(PARAMS["bg_blur_size"])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Stima e rimozione dello sfondo
    background = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)
    no_bg = cv2.subtract(gray, background)

    # Aumento del contrasto
    enhanced = normalization_service.clahe(no_bg, 3.0, (8, 8))

    # Rilevamento bordi
    edges = cv2.Canny(enhanced, PARAMS["canny_low"], PARAMS["canny_high"])

    # Chiusura dei bordi aperti
    kernel = np.ones((ensure_odd(PARAMS["morph_kernel_size"]),) * 2, np.uint8)
    edges_closed = cv2.morphologyEx(
        edges, cv2.MORPH_CLOSE, kernel, iterations=int(PARAMS["morph_iterations"])
    )
    return edges_closed


def find_valid_contours(preprocessed_img: np.ndarray) -> list[np.ndarray]:
    """
    Trova i contorni validi (area e circolarità minima) nell'immagine preprocessata.
    Restituisce una mappa {centro: contorno}.
    """
    all_contours, _ = cv2.findContours(
        preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    contour_list: list[np.ndarray] = []
    for cnt in all_contours:
        if (
            cv2.contourArea(cnt) >= PARAMS["min_area"]
            and contour_circularity(cnt) >= PARAMS["min_circularity"]
        ):
            contour_list.append(cnt)

    return contour_list


def extract_rois(video_path: str) -> list[Roi] | None:
    """
    Estrae un array di ROI a partire da un video raw
    """

    brightest = cv2_service.brightest_frame(video_path)
    binary = pipeline(brightest)
    contour_list = find_valid_contours(binary)

    rois: list[Roi] = []

    for idx, cnt in enumerate(contour_list):
        roi = Roi(video_path=video_path, idx=idx)
        roi.contours = cnt
        rois.append(roi)

    return rois
