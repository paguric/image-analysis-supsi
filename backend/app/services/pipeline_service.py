import cv2
import numpy as np

from app.models.roi import Roi
from app.schemas.pipeline_params import PipelineParams
from app.services import normalization_service


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


def pipeline(img: np.ndarray, params: PipelineParams = None) -> list[np.ndarray] | None:
    """
    HPF → CLAHE → Canny → Closing
    Restituisce una lista di immagini con il risultato di ciascun step.
    All'ultimo indice si trova l'immgaine binaria da cui estrarre i contorni.
    """
    # Valori di default
    if params is None:
        params = PipelineParams()

    out: list[np.ndarray] = []

    bg_blur = ensure_odd(params.bg_blur_size)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Stima e rimozione dello sfondo
    background = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)
    no_bg = cv2.subtract(gray, background)

    # Aumento del contrasto
    enhanced = normalization_service.clahe(
        no_bg,
        params.clahe_clip_limit,
        (params.clahe_grid_size, params.clahe_grid_size),
    )

    # Rilevamento bordi
    edges = cv2.Canny(enhanced, params.canny_low, params.canny_high)

    # Chiusura dei bordi aperti
    kernel = np.ones((ensure_odd(params.morph_kernel_size),) * 2, np.uint8)
    edges_closed = cv2.morphologyEx(
        edges, cv2.MORPH_CLOSE, kernel, iterations=int(params.morph_iterations)
    )

    out.append(background)
    out.append(enhanced)
    out.append(edges)
    out.append(edges_closed)

    return out


def find_valid_contours(
    preprocessed_img: np.ndarray, params: PipelineParams = None
) -> list[np.ndarray]:
    """
    Trova i contorni validi (area e circolarità minima) nell'immagine preprocessata.
    Restituisce una mappa {centro: contorno}.
    """
    # Valori di default
    if params is None:
        params = PipelineParams()

    all_contours, _ = cv2.findContours(
        preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    contour_list: list[np.ndarray] = []
    for cnt in all_contours:
        if (
            cv2.contourArea(cnt) >= params.min_area
            and contour_circularity(cnt) >= params.min_circularity
        ):
            contour_list.append(cnt)

    return contour_list


def extract_rois(frame: np.ndarray) -> list[Roi] | None:
    """
    Estrae un array di ROI a partire da un frame del video
    """

    binary = pipeline(frame)[-1]
    contour_list = find_valid_contours(binary)

    rois: list[Roi] = []

    for idx, cnt in enumerate(contour_list):
        roi = Roi(idx=idx)
        roi.contours = cnt
        rois.append(roi)

    return rois
