import cv2
import av
import numpy as np
import sys

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
video_to_analyze_path = "../../video/dopo.avi"
WINDOW_NAME = "Contour Tuner"
PANEL_WIDTH = 420          # larghezza pannello slider a destra

# ─────────────────────────────────────────────
# PARAMETRI DEFAULT  (nome, valore, min, max, scala)
# scala: il valore reale = slider_val / scala
# ─────────────────────────────────────────────
PARAMS = {
    "bg_blur_size":           {"val": 101, "min": 1,   "max": 201, "scale": 1,    "step": 2},
    "canny_low":              {"val": 1,   "min": 0,   "max": 255, "scale": 1,    "step": 1},
    "canny_high":             {"val": 120, "min": 0,   "max": 255, "scale": 1,    "step": 1},
    "bilateral_d":            {"val": 9,   "min": 1,   "max": 25,  "scale": 1,    "step": 1},
    "bilateral_sigma_color":  {"val": 30,  "min": 1,   "max": 150, "scale": 1,    "step": 1},
    "bilateral_sigma_space":  {"val": 20,  "min": 1,   "max": 150, "scale": 1,    "step": 1},
    "morph_kernel_size":      {"val": 3,   "min": 1,   "max": 15,  "scale": 1,    "step": 2},
    "morph_iterations":       {"val": 2,   "min": 1,   "max": 10,  "scale": 1,    "step": 1},
    "min_area":               {"val": 200, "min": 0,   "max": 5000,"scale": 1,    "step": 1},
    "min_circularity":        {"val": 70,  "min": 0,   "max": 100, "scale": 100,  "step": 1},
}

# Manteniamo i valori correnti degli slider
current = {k: v["val"] for k, v in PARAMS.items()}

# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def apply_clahe_gray(img, clip_limit=3.0, tile=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile)
    return clahe.apply(img)


def ensure_odd(v):
    """Assicura che un kernel size sia dispari e >= 1"""
    v = max(1, int(v))
    return v if v % 2 == 1 else v + 1


# ─────────────────────────────────────────────
# ANALISI VIDEO
# ─────────────────────────────────────────────

def brightest_frame(video_path: str):
    brightest_index = 0
    max_brightness = -1
    container = av.open(video_path)
    stream = container.streams.video[0]
    for i, frame in enumerate(container.decode(stream)):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean()
        if brightness > max_brightness:
            max_brightness = brightness
            brightest_index = i
    container.close()
    return brightest_index, max_brightness


def extract_frame(video_path: str, frame_idx: int):
    container = av.open(video_path)
    stream = container.streams.video[0]
    if frame_idx >= stream.frames or frame_idx < 0:
        container.close()
        return None
    container.seek(frame_idx, stream=stream)
    av_frame = next(container.decode(stream))
    frame = av_frame.to_ndarray(format="bgr24")
    container.close()
    return frame


# ─────────────────────────────────────────────
# COMPUTE CONTOURS
# ─────────────────────────────────────────────

def compute_contours(img, p):
    bg_blur  = ensure_odd(p["bg_blur_size"])
    morph_k  = ensure_odd(p["morph_kernel_size"])
    min_circ = p["min_circularity"] / PARAMS["min_circularity"]["scale"]

    gray        = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    background  = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)
    gray_no_bg  = cv2.subtract(gray, background)
    gray_norm   = cv2.normalize(gray_no_bg, None, 0, 255, cv2.NORM_MINMAX)
    gray_enh    = apply_clahe_gray(gray_norm)

    blurred = cv2.bilateralFilter(
        gray_enh,
        d=int(p["bilateral_d"]),
        sigmaColor=p["bilateral_sigma_color"],
        sigmaSpace=p["bilateral_sigma_space"]
    )

    edges = cv2.Canny(blurred, p["canny_low"], p["canny_high"])

    kernel       = np.ones((morph_k, morph_k), np.uint8)
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel,
                                    iterations=int(p["morph_iterations"]))

    contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    output  = img.copy()
    matched = 0

    for cnt in contours:
        area      = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, closed=True)
        if perimeter < 1e-6:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity >= min_circ and area >= p["min_area"]:
            cv2.drawContours(output, [cnt], -1, (0, 255, 0), 2)
            matched += 1

    return output, matched, len(contours)


# ─────────────────────────────────────────────
# SLIDER PANEL (disegnato con OpenCV)
# ─────────────────────────────────────────────

SLIDER_H      = 42
PANEL_TOP_PAD = 20
PANEL_BOT_PAD = 20
LABEL_W       = 220
BAR_X         = LABEL_W + 10
BAR_W         = 140
KNOB_R        = 8
VALUE_X       = BAR_X + BAR_W + 12

COL_BG        = (18,  18,  18)
COL_TRACK     = (55,  55,  55)
COL_FILL      = (0,  200,  80)
COL_KNOB      = (255, 255, 255)
COL_TEXT      = (220, 220, 220)
COL_DIM       = (110, 110, 110)
COL_HEADER    = (0,  200,  80)

FONT          = cv2.FONT_HERSHEY_SIMPLEX


def draw_panel(p, n_matched, n_total):
    keys   = list(PARAMS.keys())
    height = PANEL_TOP_PAD + len(keys) * SLIDER_H + PANEL_BOT_PAD + 60
    panel  = np.full((height, PANEL_WIDTH, 3), COL_BG, dtype=np.uint8)

    # ── Header ──
    cv2.putText(panel, "CONTOUR TUNER", (16, 18),
                FONT, 0.52, COL_HEADER, 1, cv2.LINE_AA)

    for i, key in enumerate(keys):
        info  = PARAMS[key]
        raw   = p[key]
        real  = raw / info["scale"]
        y_ctr = PANEL_TOP_PAD + i * SLIDER_H + SLIDER_H // 2

        # Label
        label = key.replace("_", " ")
        cv2.putText(panel, label, (8, y_ctr + 5),
                    FONT, 0.38, COL_TEXT, 1, cv2.LINE_AA)

        # Track
        bar_y = y_ctr
        cv2.line(panel, (BAR_X, bar_y), (BAR_X + BAR_W, bar_y),
                 COL_TRACK, 4, cv2.LINE_AA)

        # Fill
        t     = (raw - info["min"]) / max(info["max"] - info["min"], 1)
        fill_x = int(BAR_X + t * BAR_W)
        if fill_x > BAR_X:
            cv2.line(panel, (BAR_X, bar_y), (fill_x, bar_y),
                     COL_FILL, 4, cv2.LINE_AA)

        # Knob
        cv2.circle(panel, (fill_x, bar_y), KNOB_R, COL_KNOB, -1, cv2.LINE_AA)
        cv2.circle(panel, (fill_x, bar_y), KNOB_R, COL_FILL,  2, cv2.LINE_AA)

        # Value
        disp = f"{real:.2f}" if info["scale"] != 1 else f"{int(raw)}"
        cv2.putText(panel, disp, (VALUE_X, y_ctr + 5),
                    FONT, 0.42, COL_DIM, 1, cv2.LINE_AA)

    # ── Stats footer ──
    fy = PANEL_TOP_PAD + len(keys) * SLIDER_H + 24
    cv2.putText(panel, f"Matched : {n_matched}", (16, fy),
                FONT, 0.45, COL_HEADER, 1, cv2.LINE_AA)
    cv2.putText(panel, f"Total   : {n_total}",  (16, fy + 22),
                FONT, 0.45, COL_DIM,    1, cv2.LINE_AA)
    cv2.putText(panel, "DRAG SLIDERS  |  Q = quit", (16, fy + 46),
                FONT, 0.36, COL_DIM, 1, cv2.LINE_AA)

    return panel


# ─────────────────────────────────────────────
# MOUSE INTERACTION
# ─────────────────────────────────────────────

dragging_key  = None
img_width_ref = [0]   # larghezza dell'immagine nel canvas (aggiornata a runtime)


def slider_y_center(idx, panel_top_pad=PANEL_TOP_PAD, slider_h=SLIDER_H):
    return panel_top_pad + idx * slider_h + slider_h // 2


def key_from_y(my):
    keys = list(PARAMS.keys())
    for i, key in enumerate(keys):
        yc = slider_y_center(i)
        if abs(my - yc) <= SLIDER_H // 2:
            return key, i
    return None, -1


def x_to_val(mx, key):
    info  = PARAMS[key]
    # mx relativo alla barra (offset dal pannello, già sottratto img_width)
    t     = np.clip((mx - BAR_X) / BAR_W, 0.0, 1.0)
    raw   = info["min"] + t * (info["max"] - info["min"])
    raw   = round(raw / info["step"]) * info["step"]
    # bg_blur e morph_kernel devono essere dispari
    if key in ("bg_blur_size", "morph_kernel_size"):
        raw = ensure_odd(raw)
    return int(np.clip(raw, info["min"], info["max"]))


def on_mouse(event, x, y, flags, param):
    global dragging_key
    iw = img_width_ref[0]
    # Il pannello slider è a destra dell'immagine
    px = x - iw   # coordinata x nel pannello
    if px < 0:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        key, _ = key_from_y(y)
        if key:
            dragging_key = key
            current[key] = x_to_val(px, key)

    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
        if dragging_key:
            current[dragging_key] = x_to_val(px, dragging_key)

    elif event == cv2.EVENT_LBUTTONUP:
        dragging_key = None


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def print_params(p, matched):
    print("\n" + "─" * 50)
    print(f"  Contorni validi rilevati: {matched}")
    print("─" * 50)
    for key, info in PARAMS.items():
        real = p[key] / info["scale"]
        disp = f"{real:.2f}" if info["scale"] != 1 else f"{int(p[key])}"
        print(f"  {key:<26} = {disp}")
    print("─" * 50)


def main():
    print("Caricamento frame più luminoso...")
    try:
        brightest_f, brightness = brightest_frame(video_to_analyze_path)
        print(f"Frame più luminoso: {brightest_f}  (brightness: {brightness:.2f})")
        source_img = extract_frame(video_to_analyze_path, brightest_f)
        if source_img is None:
            raise RuntimeError("Frame non estratto")
    except Exception as e:
        print(f"[ERRORE] {e}")
        print("Carico immagine demo (noise)...")
        source_img = np.random.randint(30, 80, (600, 800, 3), dtype=np.uint8)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1400, 800)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    prev_params   = {}
    last_matched  = 0
    last_total    = 0
    result_img    = source_img.copy()

    print_params(current, 0)

    while True:
        # Ricalcola solo se i parametri sono cambiati
        if current != prev_params:
            result_img, last_matched, last_total = compute_contours(source_img, dict(current))
            print_params(current, last_matched)
            prev_params = dict(current)

        # Ridimensiona immagine a altezza fissa per il layout
        panel = draw_panel(current, last_matched, last_total)
        ph    = panel.shape[0]
        ih    = source_img.shape[0]
        scale = ph / ih
        disp  = cv2.resize(result_img, (int(result_img.shape[1] * scale), ph))
        img_width_ref[0] = disp.shape[1]

        # Affianca immagine + pannello
        canvas = np.hstack([disp, panel])
        cv2.imshow(WINDOW_NAME, canvas)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    print("\nParametri finali:")
    print_params(current, last_matched)


if __name__ == "__main__":
    main()