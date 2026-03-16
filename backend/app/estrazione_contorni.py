import cv2
import numpy as np
import os
from scipy.optimize import linear_sum_assignment
from typing import TypedDict
from typing import TypeAlias
from app import cv2_utils
from app import norm


# ─────────────────────────────────────────────
#  TIPI
# ─────────────────────────────────────────────

class MatchedContour(TypedDict):
    center:  tuple[int, int]
    contour: np.ndarray

Color: TypeAlias = tuple[int, int, int]

# ─────────────────────────────────────────────
#  COSTANTI COLORE
# ─────────────────────────────────────────────

BLUE:   Color = (255, 0, 0)
RED:    Color = (0, 0, 255)
GREEN:  Color = (0, 255, 0)
YELLOW: Color = (0, 255, 255)
WHITE:  Color = (255, 255, 255)
BLACK:  Color = (0, 0, 0)

PARAMS = {
    "bg_blur_size":     101,
    "canny_low":        0,
    "canny_high":       0,
    "clahe_grid_dim":   8,
    "morph_kernel_size": 3,
    "morph_iterations":  4,
    "min_area":          5000,
    "min_circularity":   0.10,
}

# spazio tra immagini
BORDER = 40

# altezza fascia titolo
TITLE_BAR = 200


# ─────────────────────────────────────────────
#  HELPERS GEOMETRICI
# ─────────────────────────────────────────────

def ensure_odd(v):
    v = max(1, int(v))
    return v if v % 2 == 1 else v + 1


def contour_center(contour: np.ndarray) -> tuple[int, int]:
    x, y, w, h = cv2.boundingRect(contour)
    return x + w // 2, y + h // 2


def contour_centroid(contour: np.ndarray) -> tuple[int, int] | None:
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])


def contour_circularity(contour: np.ndarray) -> float:
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
    return np.hstack([img_left, img_right])




# ─────────────────────────────────────────────
#  HELPERS VISUALIZZAZIONE GRIGLIA
# ─────────────────────────────────────────────

def to_bgr(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img.copy()


def add_title(img, text):
    h, w = img.shape[:2]
    title = np.ones((TITLE_BAR, w, 3), dtype=np.uint8) * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = w / 600
    thickness = int(font_scale * 4)
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = (w - tw) // 2
    y = TITLE_BAR // 2 + th // 2
    cv2.putText(title, text, (x, y),
                font, font_scale, (0, 0, 255),
                thickness, cv2.LINE_AA)
    return np.vstack((title, img))


def add_border(img):
    return cv2.copyMakeBorder(
        img,
        BORDER, BORDER,
        BORDER, BORDER,
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255)
    )




# ─────────────────────────────────────────────
#  MATCHING DEI CONTORNI (Hungarian algorithm)
# ─────────────────────────────────────────────

def match_contours_by_center(
    map1: dict[tuple[int, int], np.ndarray],
    map2: dict[tuple[int, int], np.ndarray]
) -> tuple[dict[int, MatchedContour], dict[int, MatchedContour]]:
    centers1, centers2 = list(map1.keys()), list(map2.keys())

    if not centers1 or not centers2:
        return {}, {}

    dist_matrix = np.array([
        [np.hypot(x1 - x2, y1 - y2) for (x2, y2) in centers2]
        for (x1, y1) in centers1
    ])

    rows, cols = linear_sum_assignment(dist_matrix)

    result1, result2 = {}, {}
    for idx, (r, c) in enumerate(zip(rows, cols)):
        result1[idx] = {"center": centers1[r], "contour": map1[centers1[r]]}
        result2[idx] = {"center": centers2[c], "contour": map2[centers2[c]]}

    return result1, result2




# ─────────────────────────────────────────────
#  RILEVAMENTO CONTORNI
# ─────────────────────────────────────────────

def find_valid_contours(
    preprocessed_img: np.ndarray,
    p: dict[str, int | float]
) -> tuple[dict[tuple[int, int], np.ndarray], int]:
    all_contours, _ = cv2.findContours(
        preprocessed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    contour_map = {}
    for cnt in all_contours:
        if cv2.contourArea(cnt) >= p["min_area"] and \
           contour_circularity(cnt) >= p["min_circularity"]:
            contour_map[contour_center(cnt)] = cnt

    return contour_map, len(all_contours)




# ─────────────────────────────────────────────
#  POST PROCESSING
# ─────────────────────────────────────────────

def compare_rois_test(
    img_prima: np.ndarray,
    img_dopo: np.ndarray,
    matched_prima: dict[int, MatchedContour],
    matched_dopo: dict[int, MatchedContour]
) -> np.ndarray:
    output = np.zeros_like(img_prima, dtype=np.float32)
    peso   = np.zeros(img_prima.shape[:2], dtype=np.float32)

    for idx in matched_prima:
        if idx not in matched_dopo:
            continue

        contour_l = matched_prima[idx]["contour"]
        contour_r = matched_dopo[idx]["contour"]

        (cx_l, cy_l), radius_l = cv2.minEnclosingCircle(contour_l)
        (cx_r, cy_r), radius_r = cv2.minEnclosingCircle(contour_r)
        cx_l, cy_l = int(cx_l), int(cy_l)
        cx_r, cy_r = int(cx_r), int(cy_r)
        radius = int(max(radius_l, radius_r))

        h, w = img_prima.shape[:2]
        x0 = max(cx_l - radius, 0)
        y0 = max(cy_l - radius, 0)
        x1 = min(cx_l + radius, w)
        y1 = min(cy_l + radius, h)

        dx = cx_l - cx_r
        dy = cy_l - cy_r

        x0_r = max(x0 - dx, 0)
        y0_r = max(y0 - dy, 0)
        x1_r = min(x1 - dx, w)
        y1_r = min(y1 - dy, h)

        patch_prima = img_prima[y0:y1,     x0:x1    ].astype(np.float32)
        patch_dopo  = img_dopo [y0_r:y1_r, x0_r:x1_r].astype(np.float32)

        ph = min(patch_prima.shape[0], patch_dopo.shape[0])
        pw = min(patch_prima.shape[1], patch_dopo.shape[1])
        patch_prima = patch_prima[:ph, :pw]
        patch_dopo  = patch_dopo [:ph, :pw]

        diff = np.abs(patch_prima - patch_dopo)

        maschera_locale = np.zeros((ph, pw), dtype=np.uint8)
        cv2.circle(maschera_locale, (cx_l - x0, cy_l - y0), radius, 255, -1)
        maschera_locale = maschera_locale[:ph, :pw]

        m = maschera_locale.astype(np.float32) / 255.0
        if diff.ndim == 3:
            m = m[:, :, np.newaxis]

        output[y0:y0+ph, x0:x0+pw] += diff * m
        peso  [y0:y0+ph, x0:x0+pw] += m[..., 0] if diff.ndim == 3 else m

    if output.ndim == 3:
        peso_3d = peso[:, :, np.newaxis]
        output = np.where(peso_3d > 0, output / peso_3d, 0)
    else:
        output = np.where(peso > 0, output / peso, 0)

    return np.clip(output, 0, 255).astype(np.uint8)




# ─────────────────────────────────────────────
#  VISUALIZZAZIONE CONTORNI
# ─────────────────────────────────────────────


def draw_contours_on_image(img, contour_map):
    black_img = np.zeros_like(img)
    
    for i, (center, cnt) in enumerate(contour_map.items(), start=1):
        draw_contour(black_img, cnt, color=GREEN)
        draw_bounding_box(black_img, cnt, color=YELLOW)
        draw_label(black_img, i, position=(center[0], center[1] - 10), color=YELLOW)
        draw_circle(black_img, center, color=BLUE)
        
        centroid = contour_centroid(cnt)
        if centroid:
            draw_circle(black_img, centroid, color=RED)
            
    b, g, r = cv2.split(black_img)
    alpha = cv2.max(cv2.max(b, g), r)
    _, alpha = cv2.threshold(alpha, 0, 255, cv2.THRESH_BINARY)
    transparent_img = cv2.merge((b, g, r, alpha))
            
    return transparent_img


def draw_centers_on_image(img, contour_map1, contour_map2):
    output = img.copy()
    for center, cnt in contour_map1.items():
        draw_circle(output, center, color=RED)
    for center, cnt in contour_map2.items():
        draw_circle(output, center, color=BLUE)
    return output


def draw_matched_contours(
    img: np.ndarray,
    matched_left: dict[int, MatchedContour],
    matched_right: dict[int, MatchedContour]
) -> np.ndarray:
    output = img.copy()
    for idx in matched_left:
        center_l, contour_l = matched_left[idx]["center"], matched_left[idx]["contour"]
        center_r, contour_r = matched_right[idx]["center"], matched_right[idx]["contour"]

        x, y, w, h = cv2.boundingRect(contour_l)
        draw_circle(output, center=center_l, radius=w//2, color=BLUE, filled=False)
        draw_label(output, idx, (center_l[0] - h//2, center_l[1] - h//2), BLUE, 0.6, 2)

        x, y, w, h = cv2.boundingRect(contour_r)
        draw_circle(output, center=center_l, radius=w//2, color=RED, filled=False)
        draw_label(output, idx, (center_l[0] + h//2, center_l[1] + h//2), RED, 0.6, 2)

    return output





# ─────────────────────────────────────────────
#  PIPELINE 
# ─────────────────────────────────────────────
def compute_contours(img, p):
    bg_blur  = ensure_odd(p["bg_blur_size"])
    morph_k  = ensure_odd(p["morph_kernel_size"])
    original = img.copy()

    gray         = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    background   = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)
    objects      = cv2.subtract(gray, background)
    gray_enh     = norm.clahe(objects, 3.0, (p["clahe_grid_dim"], p["clahe_grid_dim"]))
    edges = cv2.Canny(gray_enh, p["canny_low"], p["canny_high"])
    kernel       = np.ones((morph_k, morph_k), np.uint8)
    edges_closed = cv2.morphologyEx(
        edges, cv2.MORPH_CLOSE, kernel,
        iterations=int(p["morph_iterations"])
    )

    contour_map, total = find_valid_contours(edges_closed, p)
    contours = draw_contours_on_image(img, contour_map)

    return contours




def return_contours_only(video_to_analyze_path):
    
    print("Caricamento frame più luminoso...")

    try:
        brightest_f, brightness = cv2_utils.brightest_frame(video_to_analyze_path)
        print(f"Frame più luminoso: {brightest_f} brightness={brightness:.2f}")
        source_img = cv2_utils.extract_frame(video_to_analyze_path, brightest_f)
        if source_img is None:
            raise RuntimeError("Frame non estratto")
    except Exception as e:
        print("[ERRORE]", e)
        source_img = np.random.randint(30, 80, (600, 800, 3), dtype=np.uint8)


    return compute_contours(source_img, PARAMS)
    