import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
import os
from typing import TypedDict
from typing import TypeAlias
from app import cv2_utils, norm

## MODULO ANCORA DA SMEMBRARE
from app import params_config as parcon
from app import geometrical_helpers as geo_help
from app import draw_helpers as dr_help


class MatchedContour(TypedDict):
    center: tuple[int, int]
    contour: np.ndarray


Color: TypeAlias = tuple[int, int, int]

BLUE: Color = (255, 0, 0)
RED: Color = (0, 0, 255)
GREEN: Color = (0, 255, 0)
YELLOW: Color = (0, 255, 255)
WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)

# ─────────────────────────────────────────────
#  HELPERS GEOMETRICI
# ─────────────────────────────────────────────


def ensure_odd(v):
    """OpenCV richiede kernel di dimensione dispari."""
    v = max(1, int(v))
    return v if v % 2 == 1 else v + 1


def contour_center(contour: np.ndarray) -> tuple[int, int]:
    """Centro geometrico (bounding box) di un contorno."""
    x, y, w, h = cv2.boundingRect(contour)
    return x + w // 2, y + h // 2


def contour_centroid(contour: np.ndarray) -> tuple[int, int] | None:
    """Centro di massa (momenti) di un contorno."""
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])


def contour_circularity(contour: np.ndarray) -> float:
    """Quanto il contorno assomiglia a un cerchio (1.0 = cerchio perfetto)."""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, closed=True)
    if perimeter < 1e-6:
        return 0
    return 4 * np.pi * area / (perimeter**2)


# ─────────────────────────────────────────────
#  PREPROCESSING
# ─────────────────────────────────────────────


def preprocess(img, p):
    """
    Prepara l'immagine per il rilevamento dei contorni:
    rimozione sfondo → normalizzazione → CLAHE → filtro bilaterale → Canny → closing
    """
    bg_blur = ensure_odd(p["bg_blur_size"])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Stima e rimozione dello sfondo
    background = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)
    no_bg = cv2.subtract(gray, background)

    # Aumento del contrasto
    normalized = cv2.normalize(no_bg, None, 0, 255, cv2.NORM_MINMAX)
    enhanced = norm.clahe(normalized, 3.0, (8, 8))

    # Smoothing che preserva i bordi
    blurred = cv2.bilateralFilter(
        enhanced,
        d=int(p["bilateral_d"]),
        sigmaColor=p["bilateral_sigma_color"],
        sigmaSpace=p["bilateral_sigma_space"],
    )

    # Rilevamento bordi
    edges = cv2.Canny(blurred, p["canny_low"], p["canny_high"])

    # Chiusura dei bordi aperti
    kernel = np.ones((ensure_odd(p["morph_kernel_size"]),) * 2, np.uint8)
    edges_closed = cv2.morphologyEx(
        edges, cv2.MORPH_CLOSE, kernel, iterations=int(p["morph_iterations"])
    )
    return edges_closed


# ─────────────────────────────────────────────
#  RILEVAMENTO CONTORNI
# ─────────────────────────────────────────────


def find_valid_contours(
    preprocessed_img: np.ndarray, p: dict[str, int | float]
) -> tuple[dict[tuple[int, int], np.ndarray], int]:
    """
    Trova i contorni validi (area e circolarità minima) nell'immagine preprocessata.
    Restituisce una mappa {centro: contorno}.
    """
    all_contours, _ = cv2.findContours(
        preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    contour_map = {}
    for cnt in all_contours:
        if (
            cv2.contourArea(cnt) >= p["min_area"]
            and contour_circularity(cnt) >= p["min_circularity"]
        ):
            contour_map[contour_center(cnt)] = cnt

    return contour_map, len(all_contours)


# ─────────────────────────────────────────────
#  POST PROCESSING
# ─────────────────────────────────────────────


def match_contours_by_center(
    map1: dict[tuple[int, int], np.ndarray], map2: dict[tuple[int, int], np.ndarray]
) -> tuple[dict[int, MatchedContour], dict[int, MatchedContour]]:
    """
    Abbina i contorni più vicini tra due mappe {centro: contorno}.
    Se le mappe hanno dimensioni diverse, lavora solo sui min(n1, n2) contorni
    più vicini (i contorni in eccesso vengono ignorati).
    """
    centers1, centers2 = list(map1.keys()), list(map2.keys())

    dist_matrix = np.array(
        [[np.hypot(x1 - x2, y1 - y2) for (x2, y2) in centers2] for (x1, y1) in centers1]
    )

    rows, cols = linear_sum_assignment(dist_matrix)

    # Se le dimensioni sono diverse, linear_sum_assignment restituisce
    # solo min(n1, n2) coppie — quelle con distanza globalmente minima
    result1, result2 = {}, {}
    for idx, (r, c) in enumerate(zip(rows, cols)):
        result1[idx] = {"center": centers1[r], "contour": map1[centers1[r]]}
        result2[idx] = {"center": centers2[c], "contour": map2[centers2[c]]}

    return result1, result2


def compute_aligned_roi_diff(
    img_prima: np.ndarray,
    img_dopo: np.ndarray,
    matched_prima: dict[int, MatchedContour],
    matched_dopo: dict[int, MatchedContour],
) -> np.ndarray:
    """
    Calcola il differenziale tra le ROI corrispondenti di img_prima e img_dopo.
    I patch vengono estratti tramite cerchio minimo circoscritto, centrati
    sui rispettivi contorni, e sottratti pixel per pixel dentro una maschera circolare.
    """

    output = np.zeros_like(img_prima, dtype=np.float32)

    for idx in matched_prima:
        if idx not in matched_dopo:
            continue

        contour_l = matched_prima[idx]["contour"]
        contour_r = matched_dopo[idx]["contour"]

        # Cerchio minimo circoscritto a ciascun contorno
        (cx_l, cy_l), radius_l = cv2.minEnclosingCircle(contour_l)
        (cx_r, cy_r), radius_r = cv2.minEnclosingCircle(contour_r)
        cx_l, cy_l = int(cx_l), int(cy_l)
        cx_r, cy_r = int(cx_r), int(cy_r)

        # Raggio comune: il più grande dei due garantisce che entrambi i contorni
        # siano interamente contenuti nel patch
        radius = int(max(radius_l, radius_r))
        size = (2 * radius, 2 * radius)

        # Estrazione dei patch centrati sui rispettivi contorni.
        # getRectSubPix gestisce i bordi per interpolazione, evitando clipping.
        patch_prima = cv2.getRectSubPix(img_prima, size, (cx_l, cy_l)).astype(
            np.float32
        )
        patch_dopo = cv2.getRectSubPix(img_dopo, size, (cx_r, cy_r)).astype(np.float32)

        # Differenza pixel per pixel
        diff = patch_dopo - patch_prima

        # Maschera circolare centrata nel patch: esclude gli angoli del quadrato
        maschera = np.zeros((2 * radius, 2 * radius), dtype=np.uint8)
        cv2.circle(maschera, (radius, radius), radius, 255, -1)
        m = maschera.astype(np.float32) / 255.0
        if diff.ndim == 3:
            m = m[:, :, np.newaxis]

        # Scrittura del differenziale mascherato nella posizione del contorno "prima"
        x0, y0 = cx_l - radius, cy_l - radius
        output[y0 : y0 + 2 * radius, x0 : x0 + 2 * radius] = diff * m

    return np.clip(output, 0, 255).astype(np.uint8)


# ─────────────────────────────────────────────
#  PARAMETRI
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────


def load_brightest_frame(video_path):
    idx, _ = cv2_utils.brightest_frame(video_path)
    return cv2_utils.extract_frame(video_path, idx)


# TODO
# si potrebbe modificare analyze() per accettare bytes/numpy array oppure UploadFile
def analyze(
    video_prima_path: str,
    video_dopo_path: str,
    diff_path: str,
    # qua andranno passati eventualmente i parametri!
):
    """
    Questa funzione esegue l'intera pipeline
    Prende come input i due video, salvati su disco al path passato come parametro e il path dove salvare il video differenziale
    diff_path dev'essere nel formato "percorso/diff/nome_file.avi"
    """

    # TODO aggiungere controllo/test per verificare che diff_path sia valido

    # Caricamento frame più luminoso per ciascuna immagine
    idx, _ = cv2_utils.brightest_frame(video_prima_path)
    img_prima = cv2_utils.extract_frame(video_prima_path, idx)

    idx, _ = cv2_utils.brightest_frame(video_dopo_path)
    img_dopo = cv2_utils.extract_frame(video_dopo_path, idx)

    # Calcolo dei contorni
    contour_map_prima, total_prima = find_valid_contours(
        preprocess(img_prima, PARAMS), PARAMS
    )

    contour_map_dopo, total_dopo = find_valid_contours(
        preprocess(img_dopo, PARAMS), PARAMS
    )

    # Matching degli indici
    matched_prima, matched_dopo = match_contours_by_center(
        contour_map_prima, contour_map_dopo
    )

    # Calcolo differenziale a partire dai contorni trovati sul frame più luminoso
    metadati_prima = cv2_utils.get_video_info(video_prima_path)
    metadati_dopo = cv2_utils.get_video_info(video_dopo_path)

    fps = min(metadati_prima["fps"], metadati_dopo["fps"])
    width = min(metadati_prima["width"], metadati_dopo["width"])
    height = min(metadati_prima["height"], metadati_dopo["height"])

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(diff_path, fourcc, fps, (width, height))

    for i in range(int(fps)):
        diff = compute_aligned_roi_diff(
            cv2_utils.extract_frame(video_prima_path, i),
            cv2_utils.extract_frame(video_dopo_path, i),
            matched_prima,
            matched_dopo,
        )
        out.write(diff)

    out.release()
