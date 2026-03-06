import cv2
import av
import time

"""
DOVREBBE SOLAMENTE ESSERE UN TENTATIVO DI RENDERE PIU' SMART IL PRIMO CODICE DELLA CONTOUR DETECTION MA L'HO RUNNATO
E FA ABBASTANZA PENA
"""

# -------------------------------
# Utility: stampa durata
# -------------------------------
def time_convert(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"

# -------------------------------
# Apertura video
# -------------------------------
container = av.open(R"../video/dopo.avi")
stream = container.streams.video[0]

start_perf = time.perf_counter()
start_time = time.time()

cv2.namedWindow("video", cv2.WINDOW_NORMAL)
cv2.resizeWindow("video", 1400, 800)

# -------------------------------
# Riproduzione frame-by-frame
# -------------------------------
for frame in container.decode(stream):

    # PyAV → OpenCV
    img = frame.to_ndarray(format="bgr24")

    # timestamp reale del frame
    t = float(frame.pts * frame.time_base)

    # -------------------------------
    # PREPROCESSING
    # -------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # aumento contrasto locale (FONDAMENTALE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # riduzione rumore
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # -------------------------------
    # THRESHOLD ADATTIVO
    # -------------------------------
    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # -------------------------------
    # CONTORNI
    # -------------------------------
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,          # solo contorni principali
        cv2.CHAIN_APPROX_SIMPLE     # meno rumore
    )

    # disegno contorni
    output = img.copy()
    cv2.drawContours(output, contours, -1, (0, 255, 0), 2)

    # -------------------------------
    # Sync realtime
    # -------------------------------
    while time.perf_counter() - start_perf < t:
        time.sleep(0.001)

    cv2.imshow("video", output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

end_time = time.time()
print("Durata video:", time_convert(end_time - start_time))

cv2.destroyAllWindows()