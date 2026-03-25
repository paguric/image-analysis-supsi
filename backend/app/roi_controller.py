import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

class ROI:

    def __init__(self, video_path: str, idx: int):
        self.video_path = video_path
        self.idx = idx

    def set_center(self, center: tuple[int, int]):
        self.center = center

    def set_contours(self, contours: np.ndarray):
        self.contours = contours


def match_rois_by_center(roi_1: list[ROI], roi_2: list[ROI]):
    """
    Abbina le ROI in base alla distanza dei loro centri.
    Se il numero di ROI è diverso, tiene solo le min(n1, n2) ROI più vicine
    e elimina le ROI in eccesso dalle liste originali.
    
    ATTENZIONE: MODIFICA IN PLACE le liste roi_1 e roi_2!
    """

    centers1 = [roi.center for roi in roi_1]
    centers2 = [roi.center for roi in roi_2]

    dist_matrix = np.array(
        [[np.hypot(x1 - x2, y1 - y2) for (x2, y2) in centers2] for (x1, y1) in centers1]
    )

    rows, cols = linear_sum_assignment(dist_matrix)

    matched_roi1 = [roi_1[r] for r in rows]
    matched_roi2 = [roi_2[c] for c in cols]

    # ROI dalla prima lista prende l'indice della seconda
    for roi_a, roi_b in zip(matched_roi1, matched_roi2):
        roi_a.idx = roi_b.idx

    # Eliminazione ROI in eccesso
    roi_1[:] = matched_roi1
    roi_2[:] = matched_roi2


def compute_aligned_roi_diff(
    img_prima: np.ndarray,
    img_dopo: np.ndarray,
    roi_prima: list[ROI],
    roi_dopo: list[ROI],
) -> np.ndarray:
    """
    Calcola il differenziale tra le ROI corrispondenti di img_prima e img_dopo.
    I patch vengono estratti tramite cerchio minimo circoscritto, centrati
    sui rispettivi contorni, e sottratti pixel per pixel dentro una maschera circolare.
    
    Nota: si assume che roi_prima e roi_dopo siano già allineate 
          (stesso numero di elementi e stesso ordine dopo il matching).
    """
    if len(roi_prima) != len(roi_dopo):
        raise ValueError("Le due liste di ROI devono avere la stessa lunghezza dopo il matching")

    output = np.zeros_like(img_prima, dtype=np.float32)

    for roi_l, roi_r in zip(roi_prima, roi_dopo):
        # Prendiamo i contorni direttamente dagli oggetti ROI
        contour_l = roi_l.contours
        contour_r = roi_r.contours

        # Cerchio minimo circoscritto a ciascun contorno
        (cx_l, cy_l), radius_l = cv2.minEnclosingCircle(contour_l)
        (cx_r, cy_r), radius_r = cv2.minEnclosingCircle(contour_r)

        cx_l, cy_l = int(cx_l), int(cy_l)
        cx_r, cy_r = int(cx_r), int(cy_r)

        # Raggio comune (il più grande dei due)
        radius = int(max(radius_l, radius_r))
        size = (2 * radius, 2 * radius)

        # Estrazione dei patch centrati
        patch_prima = cv2.getRectSubPix(img_prima, size, (cx_l, cy_l)).astype(np.float32)
        patch_dopo  = cv2.getRectSubPix(img_dopo,  size, (cx_r, cy_r)).astype(np.float32)

        # Differenza pixel-per-pixel
        diff = patch_dopo - patch_prima

        # Maschera circolare per escludere gli angoli
        maschera = np.zeros((2 * radius, 2 * radius), dtype=np.uint8)
        cv2.circle(maschera, (radius, radius), radius, 255, -1)
        m = maschera.astype(np.float32) / 255.0

        if diff.ndim == 3:
            m = m[:, :, np.newaxis]

        # Scrittura del differenziale mascherato nella posizione originale del contorno "prima"
        x0, y0 = cx_l - radius, cy_l - radius
        output[y0 : y0 + 2 * radius, x0 : x0 + 2 * radius] = diff * m

    return np.clip(output, 0, 255).astype(np.uint8)