import cv2
import numpy as np
import os
from scipy.optimize import linear_sum_assignment
from app import cv2_utils
from app import norm
from app import params_config as parcon
from app import geometrical_helpers as geo_help
from app import draw_helpers as dr_help


#   (Hungarian algorithm)
def match_contours_by_center(
    map1: dict[tuple[int, int], np.ndarray],
    map2: dict[tuple[int, int], np.ndarray]
) -> tuple[dict[int, parcon.MatchedContour], dict[int, parcon.MatchedContour]]:
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
           geo_help.contour_circularity(cnt) >= p["min_circularity"]:
            contour_map[geo_help.contour_center(cnt)] = cnt

    return contour_map, len(all_contours)




def compute_contours(img, p):
    bg_blur  = geo_help.ensure_odd(p["bg_blur_size"])
    morph_k  = geo_help.ensure_odd(p["morph_kernel_size"])
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
    contours = dr_help.draw_contours_on_image(img, contour_map)

    return contours




def return_computed_contours(video_to_analyze_path):
    
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


    return compute_contours(source_img, parcon.PARAMS)
    