import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

from app.services import video_metadata_service
from app.models.roi import Roi
from app.models.enums import Analisi
from app.schemas.roi import RoiResponse
from app.repositories.roi_repo import RoiRepository


def add_roi(repo: RoiRepository, roi: Roi):
    return repo.add(roi)


def get_roi(repo: RoiRepository, idx: int, analisi: Analisi) -> list[Roi]:
    return repo.get(idx, analisi)


def get_roi_list(repo: RoiRepository, analisi: Analisi) -> list[Roi]:
    return repo.list(analisi)


def roi_to_response(roi: Roi) -> RoiResponse:
    center = roi.get_center() if roi.contours_data else None

    # np.ndarray di shape (N, 1, 2) -> lista di punti [[x, y], ...]
    contours_list = None
    if roi.contours_data is not None:
        contours_list = roi.contours.reshape(-1, 2).tolist()

    return RoiResponse(
        id=roi.id,
        idx=roi.idx,
        video_path=roi.video_path,
        fase=roi.fase,
        center_x=center[0] if center else None,
        center_y=center[1] if center else None,
        has_contours=roi.contours_data is not None,
        contours=contours_list,
    )


def response_to_roi(response: RoiResponse) -> Roi:
    contours = None
    if response.contours is not None:
        # [[x, y], ...] -> np.ndarray shape (N, 1, 2)
        contours = np.array(response.contours, dtype=np.int32).reshape(-1, 1, 2)

    roi = Roi(
        id=response.id,
        idx=response.idx,
        video_path=response.video_path,
        fase=response.fase,
    )
    if contours is not None:
        roi.contours = contours
    return roi


def match_rois_by_center(
    roi_1: list[Roi], roi_2: list[Roi]
) -> tuple[list[Roi], list[Roi]]:
    """
    Abbina le Roi in base alla distanza dei loro centri.
    Se il numero di Roi è diverso, tiene solo le min(n1, n2) Roi più vicine.

    Restituisce due nuove liste di Roi abbinate, senza modificare le liste originali.
    """

    centers1 = [roi.get_center() for roi in roi_1]
    centers2 = [roi.get_center() for roi in roi_2]

    dist_matrix = np.array(
        [[np.hypot(x1 - x2, y1 - y2) for (x2, y2) in centers2] for (x1, y1) in centers1]
    )

    rows, cols = linear_sum_assignment(dist_matrix)

    matched_roi1 = [roi_1[r] for r in rows]
    matched_roi2 = [roi_2[c] for c in cols]

    # Le roi della prima lista prendono l'indice di quelle della 2a
    for roi_a, roi_b in zip(matched_roi1, matched_roi2):
        roi_a.idx = roi_b.idx

    return matched_roi1, matched_roi2


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


def get_min_size(patch1: np.ndarray, patch2: np.ndarray) -> int:
    """
    Calcola la dimensione minima fra le due patch.
    """

    # Nota: le patch sono quadrate: h1 == w1
    h1, w1 = patch1.shape[:2]
    h2, w2 = patch2.shape[:2]

    min_size = min(w1, w2)

    # Forza dimensioni dispari: garantisce un centro esatto (pixel centrale unico)
    if min_size % 2 == 0:
        min_size += 1

    return min_size


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
    ph, pw = patch.shape[:2]

    # Se la patch è più grande del canvas, ritaglia dal centro
    if ph > canvas_size or pw > canvas_size:
        cy, cx = ph // 2, pw // 2
        half = canvas_size // 2
        patch = patch[cy - half : cy + half + 1, cx - half : cx + half + 1]
        ph, pw = patch.shape[:2]

    # Crea canvas nero con gli stessi canali della patch
    if patch.ndim == 3:
        canvas = np.zeros((canvas_size, canvas_size, patch.shape[2]), dtype=patch.dtype)
    else:
        canvas = np.zeros((canvas_size, canvas_size), dtype=patch.dtype)

    # Offset per centrare: quanto spazio lasciare attorno alla patch
    offset = (canvas_size - pw) // 2

    canvas[offset : offset + ph, offset : offset + pw] = patch

    return canvas


def compute_aligned_roi_diff(
    roi_prima: list[Roi], roi_dopo: list[Roi], frame: int
) -> np.ndarray:
    """
    Calcola il differenziale tra le Roi corrispondenti di img_prima e img_dopo.
    I patch vengono estratti tramite cerchio minimo circoscritto, centrati
    sui rispettivi contorni, e sottratti pixel per pixel dentro una maschera circolare.

    Nota: si assume che roi_prima e roi_dopo siano già allineate
          (stesso numero di elementi e stesso ordine dopo il matching).
    """
    if len(roi_prima) != len(roi_dopo):
        raise ValueError(
            "Le due liste di Roi devono avere la stessa lunghezza dopo il matching"
        )

    output = np.zeros_like(
        video_metadata_service.extract_frame(roi_prima[0].video_path, frame),
        dtype=np.float32,
    )

    for roi_l, roi_r in zip(roi_prima, roi_dopo):
        patch_l = roi_l.get_pixels(frame)
        patch_r = roi_r.get_pixels(frame)

        common_size = get_common_size(patch_l, patch_r)
        patch_l = center_patch_on_canvas(patch_l, common_size)
        patch_r = center_patch_on_canvas(patch_r, common_size)

        ## Calcola maschera con regione comune per le due aree
        mask_l = np.zeros((common_size, common_size), dtype=np.uint8)
        mask_r = np.zeros((common_size, common_size), dtype=np.uint8)

        cv2.drawContours(mask_l, [roi_l.get_local_contours()], 0, 255, -1)
        cv2.drawContours(mask_r, [roi_r.get_local_contours()], 0, 255, -1)
        common_mask = cv2.bitwise_and(mask_r, mask_r)

        # Applica la maschera sulle patch
        patch_l = cv2.bitwise_and(patch_l, patch_l, mask=common_mask)
        patch_r = cv2.bitwise_and(patch_r, patch_r, mask=common_mask)

        diff = patch_r.astype(np.float32) - patch_l.astype(np.float32)

        # Scrittura del differenziale mascherato nella posizione originale del contorno "prima"
        cx_l, cy_l = roi_l.get_center()
        x0, y0 = cx_l - common_size // 2, cy_l - common_size // 2
        output[y0 : y0 + common_size, x0 : x0 + common_size] = diff

    return np.clip(output, 0, 255).astype(np.uint8)
