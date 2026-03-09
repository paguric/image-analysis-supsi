import cv2
import numpy as np
import cv2_utils
import norm

video_to_analyze_path = "video/dopo.avi"

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

# spazio tra immagini
BORDER = 40

# altezza fascia titolo
TITLE_BAR = 200


def ensure_odd(v):
    v = max(1, int(v))
    return v if v % 2 == 1 else v + 1


def to_bgr(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img.copy()


def add_title(img, text):

    h, w = img.shape[:2]

    # crea barra bianca sopra
    title = np.ones((TITLE_BAR, w, 3), dtype=np.uint8) * 255

    font = cv2.FONT_HERSHEY_SIMPLEX

    # scala dinamica (testo enorme)
    font_scale = w / 600
    thickness = int(font_scale * 4)

    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

    x = (w - tw) // 2
    y = TITLE_BAR // 2 + th // 2

    cv2.putText(title, text, (x, y),
                font, font_scale, (0,0,255),
                thickness, cv2.LINE_AA)

    return np.vstack((title, img))


def add_border(img):
    return cv2.copyMakeBorder(
        img,
        BORDER, BORDER,
        BORDER, BORDER,
        cv2.BORDER_CONSTANT,
        value=(255,255,255)
    )


def compute_contours(img, p):

    bg_blur  = ensure_odd(p["bg_blur_size"])
    morph_k  = ensure_odd(p["morph_kernel_size"])
    min_circ = p["min_circularity"]

    original = img.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    background = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)

    gray_no_bg = cv2.subtract(gray, background)

    gray_norm = cv2.normalize(gray_no_bg, None, 0, 255, cv2.NORM_MINMAX)

    gray_enh = norm.clahe(gray_norm, 3.0, (8,8))

    blurred = cv2.bilateralFilter(
        gray_enh,
        d=int(p["bilateral_d"]),
        sigmaColor=p["bilateral_sigma_color"],
        sigmaSpace=p["bilateral_sigma_space"]
    )

    edges = cv2.Canny(blurred, p["canny_low"], p["canny_high"])

    kernel = np.ones((morph_k, morph_k), np.uint8)

    edges_closed = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=int(p["morph_iterations"])
    )

    contours, _ = cv2.findContours(
        edges_closed,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    output = img.copy()
    matched = 0

    for cnt in contours:

        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)

        if perimeter < 1e-6:
            continue

        circularity = 4 * np.pi * area / (perimeter ** 2)

        if circularity >= min_circ and area >= p["min_area"]:
            cv2.drawContours(output, [cnt], -1, (0,255,0), 5)
            matched += 1

    steps = [
        ("Original", original),
        ("Gray", gray),
        ("Background", background),
        ("Gray - BG", gray_no_bg),
        ("Normalized", gray_norm),
        ("CLAHE", gray_enh),
        ("Bilateral Filter", blurred),
        ("Canny Edges", edges),
        ("Morph Closing", edges_closed),
        ("Valid Contours", output)
    ]

    return steps, matched, len(contours)


print("Caricamento frame più luminoso...")

try:

    brightest_f, brightness = cv2_utils.brightest_frame(video_to_analyze_path)

    print(f"Frame più luminoso: {brightest_f} brightness={brightness:.2f}")

    source_img = cv2_utils.extract_frame(video_to_analyze_path, brightest_f)

    if source_img is None:
        raise RuntimeError("Frame non estratto")

except Exception as e:

    print("[ERRORE]", e)

    source_img = np.random.randint(30,80,(600,800,3),dtype=np.uint8)


steps, matched, total = compute_contours(source_img, PARAMS)

images = []

for name, img in steps:

    img = to_bgr(img)

    img = add_title(img, name)

    img = add_border(img)

    images.append(img)


row1 = np.hstack(images[:5])
row2 = np.hstack(images[5:])

grid = np.vstack((row1,row2))


# SALVATAGGIO UNICO LOSSLESS
cv2.imwrite(
    "pipeline_steps.png",
    grid,
    [cv2.IMWRITE_PNG_COMPRESSION, 0]
)

print("Immagine salvata: pipeline_steps.png (qualità massima, lossless)")
