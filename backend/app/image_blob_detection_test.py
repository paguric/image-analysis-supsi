import cv2
import numpy as np
from PIL import Image, ImageEnhance


# ============================================================
# FUNZIONE: aumento contrasto con PILLOW
# ============================================================

def increase_brightness_pillow(img_bgr, contrast=2.0):
    """
    img_bgr: immagine OpenCV BGR (numpy array)
    contrast: fattore di contrasto (1.0 = originale)
    return: immagine OpenCV BGR
    """

    # OpenCV (BGR) -> PIL (RGB)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    # Aumento contrasto
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(contrast)

    # PIL (RGB) -> OpenCV (BGR)
    img_rgb = np.array(pil_img)
    img_bgr_out = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    return img_bgr_out


# ============================================================
# CARICAMENTO SCREENSHOT
# ============================================================

img = cv2.imread("video\\Screenshot.png")

if img is None:
    raise FileNotFoundError("Impossibile caricare Screenshot.png")

# Aumento contrasto globale (Pillow)
img = increase_brightness_pillow(img, contrast=2.5)


# ============================================================
# CONFIGURAZIONE SIMPLE BLOB DETECTOR
# ============================================================

params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 5
params.maxThreshold = 255

params.filterByArea = True
params.minArea = 50
params.maxArea = 5000

params.filterByColor = True
params.blobColor = 255  # blob chiari su sfondo scuro

params.filterByCircularity = False
params.filterByConvexity = False
params.filterByInertia = False

detector = cv2.SimpleBlobDetector_create(params)


# ============================================================
# PREPROCESSING
# ============================================================

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

clahe = cv2.createCLAHE(
    clipLimit=3.0,
    tileGridSize=(8, 8)
)
gray = clahe.apply(gray)

gray = cv2.GaussianBlur(gray, (5, 5), 0)


# ============================================================
# BLOB DETECTION
# ============================================================

keypoints = detector.detect(gray)

im_with_keypoints = cv2.drawKeypoints(
    img,
    keypoints,
    None,
    (0, 0, 255),
    cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
)


# ============================================================
# VISUALIZZAZIONE
# ============================================================

cv2.namedWindow("result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("result", 1400, 800)
cv2.imshow("result", im_with_keypoints)
cv2.waitKey(0)
cv2.destroyAllWindows()