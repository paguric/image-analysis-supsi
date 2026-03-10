import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import TypedDict
from typing import TypeAlias
from app import cv2_utils, norm

class MatchedContour(TypedDict):
    center:  tuple[int, int]
    contour: np.ndarray

Color: TypeAlias = tuple[int, int, int]

BLUE:   Color = (255, 0, 0)
RED:    Color = (0, 0, 255)
GREEN:  Color = (0, 255, 0)
YELLOW: Color = (0, 255, 255)
WHITE:  Color = (255, 255, 255)
BLACK:  Color = (0, 0, 0)

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
    area      = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, closed=True)
    if perimeter < 1e-6:
        return 0
    return 4 * np.pi * area / (perimeter ** 2)


# ─────────────────────────────────────────────
#  HELPERS DI DISEGNO
# ─────────────────────────────────────────────

def draw_contour(img, contour, color, thickness=2):
    cv2.drawContours(img, [contour], -1, color, thickness)

def draw_bounding_box(img, contour, color, thickness=2):
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

def draw_circle(img, center, radius=6, color=(255, 0, 0), filled=True):
    thickness = -1 if filled else 2
    cv2.circle(img, center, radius, color, thickness)

def draw_label(img, text, position, color, font_scale=0.6, thickness=2):
    cv2.putText(img, str(text), position,
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def draw_line(img, pt1, pt2, color, thickness=1):
    cv2.line(img, pt1, pt2, color, thickness, cv2.LINE_AA)

def side_by_side(img_left, img_right):
    """Affianca due immagini orizzontalmente."""
    return np.hstack([img_left, img_right])


# ─────────────────────────────────────────────
#  MATCHING DEI CONTORNI (Hungarian algorithm)
# ─────────────────────────────────────────────

def match_contours_by_center(
    map1: dict[tuple[int, int], np.ndarray],
    map2: dict[tuple[int, int], np.ndarray]
) -> tuple[dict[int, MatchedContour], dict[int, MatchedContour]]:
    """
    Abbina i contorni più vicini tra due mappe {centro: contorno}.
    Se le mappe hanno dimensioni diverse, lavora solo sui min(n1, n2) contorni
    più vicini (i contorni in eccesso vengono ignorati).
    """
    centers1, centers2 = list(map1.keys()), list(map2.keys())

    dist_matrix = np.array([
        [np.hypot(x1 - x2, y1 - y2) for (x2, y2) in centers2]
        for (x1, y1) in centers1
    ])

    rows, cols = linear_sum_assignment(dist_matrix)

    # Se le dimensioni sono diverse, linear_sum_assignment restituisce
    # solo min(n1, n2) coppie — quelle con distanza globalmente minima
    result1, result2 = {}, {}
    for idx, (r, c) in enumerate(zip(rows, cols)):
        result1[idx] = {"center": centers1[r], "contour": map1[centers1[r]]}
        result2[idx] = {"center": centers2[c], "contour": map2[centers2[c]]}

    return result1, result2


# ─────────────────────────────────────────────
#  PREPROCESSING
# ─────────────────────────────────────────────

def preprocess(img, p):
    """
    Prepara l'immagine per il rilevamento dei contorni:
    rimozione sfondo → normalizzazione → CLAHE → filtro bilaterale → Canny → closing
    """
    bg_blur = ensure_odd(p["bg_blur_size"])
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Stima e rimozione dello sfondo
    background  = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)
    no_bg       = cv2.subtract(gray, background)

    # Aumento del contrasto
    normalized  = cv2.normalize(no_bg, None, 0, 255, cv2.NORM_MINMAX)
    enhanced    = norm.clahe(normalized, 3.0, (8, 8))

    # Smoothing che preserva i bordi
    blurred = cv2.bilateralFilter(
        enhanced,
        d          = int(p["bilateral_d"]),
        sigmaColor = p["bilateral_sigma_color"],
        sigmaSpace = p["bilateral_sigma_space"]
    )

    # Rilevamento bordi
    edges = cv2.Canny(blurred, p["canny_low"], p["canny_high"])

    # Chiusura dei bordi aperti
    kernel       = np.ones((ensure_odd(p["morph_kernel_size"]),) * 2, np.uint8)
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel,
                                    iterations=int(p["morph_iterations"]))
    return edges_closed


# ─────────────────────────────────────────────
#  RILEVAMENTO CONTORNI
# ─────────────────────────────────────────────

def find_valid_contours(
    preprocessed_img: np.ndarray,
    p: dict[str, int | float]
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
        if cv2.contourArea(cnt) >= p["min_area"] and \
           contour_circularity(cnt)  >= p["min_circularity"]:
            contour_map[contour_center(cnt)] = cnt

    return contour_map, len(all_contours)


# ─────────────────────────────────────────────
#  VISUALIZZAZIONE
# ─────────────────────────────────────────────

def draw_contours_on_image(img, contour_map):
    """
    Disegna su una copia dell'immagine tutti i contorni validi con:
    contorno verde, bounding box gialla, centro geometrico blu, centroide rosso.
    """
    output = img.copy()

    for i, (center, cnt) in enumerate(contour_map.items(), start=1):
        draw_contour(output, cnt, color=(0, 255, 0))
        draw_bounding_box(output, cnt, color=(0, 255, 255))
        draw_label(output, i, position=(center[0], center[1] - 10), color=(0, 255, 255))
        draw_circle(output, center, color=(255, 0, 0))   # centro geometrico (blu)

        centroid = contour_centroid(cnt)
        if centroid:
            draw_circle(output, centroid, color=(0, 0, 255))  # centroide (rosso)

    return output


def draw_matched_contours(
    img: np.ndarray,
    matched_left: dict[int, MatchedContour],
    matched_right: dict[int, MatchedContour]
) -> np.ndarray:
    """
    Disegna sulla stessa immagine i centri delle due analisi come cerchi concentrici.
    Blu = prima, Rosso = dopo.
    """
    output = img.copy()

    for idx in matched_left:
        center_l, contour_l = matched_left[idx]["center"],  matched_left[idx]["contour"]
        center_r, contour_r = matched_right[idx]["center"],  matched_right[idx]["contour"]

        x, y, w, h = cv2.boundingRect(contour_l)
        draw_circle(output, center=center_l, radius=w//2, color=BLUE, filled=False)
        draw_label(output, idx, (center_l[0] - h//2, center_l[1] - h//2), BLUE, 0.6, 2)

        x, y, w, h = cv2.boundingRect(contour_r)
        draw_circle(output, center=center_l, radius=w//2, color=RED, filled=False)
        draw_label(output, idx, (center_l[0] + h//2, center_l[1] + h//2), RED, 0.6, 2)

    return output


def show(title, img, width=1200, height=700):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, width, height)
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ─────────────────────────────────────────────
#  PARAMETRI
# ─────────────────────────────────────────────

PARAMS = {
    "bg_blur_size":          101,
    "canny_low":             0,
    "canny_high":            0,
    "bilateral_d":           5,
    "bilateral_sigma_color": 50,
    "bilateral_sigma_space": 1,
    "morph_kernel_size":     3,
    "morph_iterations":      2,
    "min_area":              5000,
    "min_circularity":       0.10,
}


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def load_brightest_frame(video_path):
    idx, _ = cv2_utils.brightest_frame(video_path)
    return cv2_utils.extract_frame(video_path, idx)

img_prima = load_brightest_frame("video/prima.avi")
img_dopo  = load_brightest_frame("video/dopo.avi")

contour_map_prima, total_prima = find_valid_contours(preprocess(img_prima, PARAMS), PARAMS)
contour_map_dopo,  total_dopo  = find_valid_contours(preprocess(img_dopo,  PARAMS), PARAMS)

print(f"Prima → trovati {total_prima}, validi {len(contour_map_prima)}")
print(f"Dopo  → trovati {total_dopo},  validi {len(contour_map_dopo)}")

# Genera le immagini con i contorni disegnati sopra
img_visual_prima = draw_contours_on_image(img_prima, contour_map_prima)
img_visual_dopo  = draw_contours_on_image(img_dopo, contour_map_dopo)

# Scrittura su file
cv2.imwrite("out/analisi_prima.jpg", img_visual_prima)
cv2.imwrite("out/analisi_dopo.jpg", img_visual_dopo)

print("Immagini salvate correttamente: analisi_prima.jpg, analisi_dopo.jpg")

matched_prima, matched_dopo = match_contours_by_center(contour_map_prima, contour_map_dopo)

img = draw_matched_contours(img_prima, matched_prima, matched_dopo)
show("Contour Match", img, width=1080)