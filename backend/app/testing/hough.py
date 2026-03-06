import cv2
import av
import time
import numpy as np

video_to_analyze_path = "../../video/dopo.avi"

# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def time_convert(seconds):
    """Converte secondi in formato mm:ss"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"


def apply_clahe_gray(img):
    """Aumenta contrasto locale e luminosità su un'immagine grayscale"""
    clahe = cv2.createCLAHE(clipLimit=8.5, tileGridSize=(6, 6))
    return clahe.apply(img)


# ─────────────────────────────────────────────
# ANALISI VIDEO
# ─────────────────────────────────────────────

def brightest_frame(video_path: str) -> tuple[int, float]:
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


def extract_frame(video_path: str, frame_idx: int) -> np.ndarray | None:
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
# ELABORAZIONE IMMAGINE: Hough Circle
# ─────────────────────────────────────────────

def compute_hough_circles(
    img,
    # ──────────────────────────────────────────────────────────────
    #  Parametri principali da regolare in base al problema
    # ──────────────────────────────────────────────────────────────
    clahe_clip=2.0,                 # CLAHE: contrasto locale (1.0–4.0 tipico)
    clahe_tile=8,                   # grandezza tile CLAHE (8×8 o 16×16 comune)
    blur_kernel=9,                  # kernel Gaussian blur pre-Hough (5,7,9,11...)
    blur_sigma=2,                   # sigma blur → più alto = bordi più morbidi
    dp=1.2,                         # risoluzione accumulatore (1.0–2.0)
    min_dist=20,                    # distanza minima tra centri cerchi (pixel)
    param1=100,                     # soglia alta Canny interna (50–150)
    param2=30,                      # threshold accumulatore (20–60 critico!)
    min_radius=1,                   # raggio minimo cerchio (pixel)
    max_radius=50,                  # raggio massimo cerchio (pixel)
    draw_circle_color=(0, 255, 0),  # colore cerchio esterno (BGR)
    draw_circle_thickness=2,
    draw_center_color=(0, 0, 255),  # colore punto centrale
    draw_center_radius=3
):
    """
    Rileva cerchi tramite Hough Circle Transform (Gradient method).
    Molto sensibile ai parametri → richiede tuning per ogni tipo di immagine.

    Flusso tipico:
    1. Grayscale
    2. Miglioramento contrasto locale (CLAHE)
    3. Sfocatura Gaussiana (riduce rumore → meno falsi positivi)
    4. HoughCircles (trasformata di Hough per cerchi)
    5. Disegno cerchi + centro

    Quando HoughCircles funziona bene:
    • Cerchi ben definiti, bordi forti e uniformi
    • Poco rumore / sfondo omogeneo
    • Raggi simili tra loro

    Quando invece preferire contour-based (findContours + circolarità):
    • Cerchi parzialmente occlusi / spezzati
    • Illuminazione molto irregolare
    • Molto rumore o texture complessa

    Regole empiriche per tuning (ordine consigliato):
    1. Imposta min_radius e max_radius realistici (guarda immagine!)
    2. min_dist ≈ 1.5–2.5 × raggio medio atteso
    3. param2: valore più critico → inizia da 25–45, poi sali/scendi
    4. param1: 80–120 nella maggior parte dei casi
    5. dp: 1.0–1.5 (valori >2 perdono precisione)
    """
    # -------------------------------------------------------------------------
    # 1. Conversione in scala di grigi
    # -------------------------------------------------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # -------------------------------------------------------------------------
    # 2. Miglioramento contrasto locale (CLAHE)
    #    Aiuta molto quando l'illuminazione non è uniforme
    # -------------------------------------------------------------------------
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(clahe_tile, clahe_tile))
    gray_enhanced = clahe.apply(gray)

    # -------------------------------------------------------------------------
    # 3. Sfocatura Gaussiana pre-Hough
    #    Riduce rumore → meno falsi cerchi, ma bordi troppo morbidi → persi cerchi piccoli
    # -------------------------------------------------------------------------
    blurred = cv2.GaussianBlur(gray_enhanced, (blur_kernel, blur_kernel), blur_sigma)

    # -------------------------------------------------------------------------
    # 4. Trasformata di Hough per cerchi (metodo Gradient = unico implementato)
    # -------------------------------------------------------------------------
    circles = cv2.HoughCircles(
        image=blurred,
        method=cv2.HOUGH_GRADIENT,      # unico metodo affidabile attuale
        dp=dp,                          # 1.0 = risoluzione piena, 1.2–1.5 = compromesso velocità/precisione
        minDist=min_dist,               # ← molto importante! evita doppioni
        param1=param1,                  # soglia alta Canny interna (più basso = più bordi → più candidati)
        param2=param2,                  # soglia voti accumulatore (più basso = più cerchi, anche falsi)
        minRadius=min_radius,
        maxRadius=max_radius
    )

    # -------------------------------------------------------------------------
    # 5. Preparazione output e disegno
    # -------------------------------------------------------------------------
    output = img.copy()

    if circles is not None:
        # convertiamo in interi (Hough restituisce float)
        circles = np.uint16(np.around(circles))

        for (x, y, r) in circles[0, :]:
            # Cerchio esterno
            cv2.circle(
                output,
                center=(x, y),
                radius=r,
                color=draw_circle_color,
                thickness=draw_circle_thickness
            )
            # Piccolo cerchio al centro (utile per visualizzare)
            cv2.circle(
                output,
                center=(x, y),
                radius=draw_center_radius,
                color=draw_center_color,
                thickness=-1   # riempito
            )

    return output


# ─────────────────────────────────────────────
# VISUALIZZAZIONE
# ─────────────────────────────────────────────

def show_frame_img(img):
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img", 1400, 800)
    cv2.imshow("img", img)

    while True:
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def play_video_with_hough():
    container = av.open(video_to_analyze_path)
    stream = container.streams.video[0]

    cv2.namedWindow("video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("video", 1400, 800)

    start_perf = time.perf_counter()
    start_time = time.time()

    for frame in container.decode(stream):
        img = frame.to_ndarray(format="bgr24")
        t = float(frame.pts * frame.time_base)

        output = compute_hough_circles(img)

        while time.perf_counter() - start_perf < t:
            time.sleep(0.001)

        cv2.imshow("video", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Durata video:", time_convert(time.time() - start_time))
    cv2.destroyAllWindows()
    container.close()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

brightest_f, brightness = brightest_frame(video_to_analyze_path)
print(f"Frame più luminoso: {brightest_f} (brightness: {brightness:.2f})")

img = extract_frame(video_to_analyze_path, brightest_f)
if img is not None:
    output = compute_hough_circles(img)
    show_frame_img(output)
else:
    print("Errore: frame non estratto")

# Per riproduzione video con rilevamento cerchi:
# play_video_with_hough()