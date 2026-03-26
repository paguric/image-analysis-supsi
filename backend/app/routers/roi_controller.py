import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
from app.helpers import cv2_utils


class ROI:
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


def match_rois_by_center(roi_1: list[ROI], roi_2: list[ROI]):
    """
    Abbina le ROI in base alla distanza dei loro centri.
    Se il numero di ROI è diverso, tiene solo le min(n1, n2) ROI più vicine
    e elimina le ROI in eccesso dalle liste originali.

    ATTENZIONE: MODIFICA IN PLACE le liste roi_1 e roi_2!
    """

    centers1 = [roi.get_center() for roi in roi_1]
    centers2 = [roi.get_center() for roi in roi_2]

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


def get_common_size(patch1: np.ndarray, patch2: np.ndarray) -> int:
    """
    Calcola la dimensione comune a cui portare entrambe le patch.
    Si usa il massimo tra i lati per non perdere informazioni.
    """

    # Nota: le patch sono quadrate: h1 == w1
    h1, w1 = patch1.shape[:2]
    h2, w2 = patch2.shape[:2]

    common_size = max(w1, w2)

    # Forza dimensioni dispari: garantisce un centro esatto (pixel centrale unico)
    if common_size % 2 == 0:
        common_size += 1

    return common_size


def center_patch_on_canvas(patch: np.ndarray, canvas_size: int) -> np.ndarray:
    """
    Posiziona la patch al centro di un canvas nero della dimensione target.
    Il canvas viene riempito di zeri (nero) dove la patch non copre.

    Args:
        patch:       la patch estratta con getRectSubPix
        canvas_size: lato del canvas di destinazione

    Returns:
        canvas con la patch centrata
    """

    # Crea canvas nero con gli stessi canali della patch
    if patch.ndim == 3:
        canvas = np.zeros((canvas_size, canvas_size, patch.shape[2]), dtype=patch.dtype)
    else:
        canvas = np.zeros((canvas_size, canvas_size), dtype=patch.dtype)

    ph, pw = patch.shape[:2]

    # Offset per centrare: quanto spazio lasciare attorno alla patch
    offset = (canvas_size - pw) // 2

    canvas[offset : offset + ph, offset : offset + pw] = patch

    return canvas


def compute_aligned_roi_diff(
    roi_prima: list[ROI], roi_dopo: list[ROI], frame: int
) -> np.ndarray:
    """
    Calcola il differenziale tra le ROI corrispondenti di img_prima e img_dopo.
    I patch vengono estratti tramite cerchio minimo circoscritto, centrati
    sui rispettivi contorni, e sottratti pixel per pixel dentro una maschera circolare.

    Nota: si assume che roi_prima e roi_dopo siano già allineate
          (stesso numero di elementi e stesso ordine dopo il matching).
    """
    if len(roi_prima) != len(roi_dopo):
        raise ValueError(
            "Le due liste di ROI devono avere la stessa lunghezza dopo il matching"
        )

    output = np.zeros_like(
        cv2_utils.extract_frame(roi_prima[0].video_path, frame), dtype=np.float32
    )

    for roi_l, roi_r in zip(roi_prima, roi_dopo):
        patch_prima = roi_l.get_pixels(frame)
        patch_dopo = roi_r.get_pixels(frame)

        # Padding se i due patch non sono della stessa dimensione -prende raggio comune (il più grande dei due)
        common_size = get_common_size(patch_prima, patch_dopo)

        # La conversione a float32 non dovrebbe essere necessaria, ma permette di aumentare la precisione della differenza
        p1_centered = center_patch_on_canvas(patch_prima, common_size).astype(
            np.float32
        )
        p2_centered = center_patch_on_canvas(patch_dopo, common_size).astype(np.float32)

        diff = p2_centered - p1_centered  # oppure potremmo usare cv2.subtract()

        # Maschera circolare per escludere gli angoli
        maschera = np.zeros((common_size, common_size), dtype=np.uint8)
        cv2.circle(
            maschera, (common_size // 2, common_size // 2), common_size // 2, 255, -1
        )
        m = maschera.astype(np.float32) / 255.0

        if diff.ndim == 3:
            m = m[:, :, np.newaxis]

        # Scrittura del differenziale mascherato nella posizione originale del contorno "prima"
        cx_l, cy_l = roi_l.get_center()
        x0, y0 = cx_l - common_size // 2, cy_l - common_size // 2
        output[y0 : y0 + common_size, x0 : x0 + common_size] = diff * m

    return np.clip(output, 0, 255).astype(np.uint8)
