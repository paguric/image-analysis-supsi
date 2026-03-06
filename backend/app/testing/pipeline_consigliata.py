import cv2
import av
import time
import numpy as np

video_to_analyze_path = "../../video/dopo.avi"

# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def time_convert(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"


def apply_clahe_gray(img):
    clahe = cv2.createCLAHE(clipLimit=8.5, tileGridSize=(6, 6))
    return clahe.apply(img)


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
# IMAGE PROCESSING
# ─────────────────────────────────────────────

def compute_contours(
    img,
    # ────────────────────────────────────────────────
    #  Parametri principali che puoi modificare
    # ────────────────────────────────────────────────
    bg_blur_size=101,              # grandezza kernel sfocatura background (strano se < 51 o > 151)
    canny_low=1,                  # soglia bassa Canny → più basso = più bordi (ma più rumore)
    canny_high=120,                # soglia alta Canny → più alto = meno bordi deboli
    bilateral_d=9,                 # diametro vicinato bilateral filter (5–15 tipicamente)
    bilateral_sigma_color=30,      # quanto considerare differenza colore (più alto = più sfocatura)
    bilateral_sigma_space=20,      # quanto considerare distanza spaziale
    morph_kernel_size=7,           # dimensione kernel morfologico (3 o 5 più comune)
    morph_iterations=2,            # quante volte applicare closing
    min_area=200,                  # area minima in pixel per considerare un contorno valido
    min_circularity=0.7,           # circolarità minima (1 = cerchio perfetto, 0.7 ≈ ellissi decenti)
    draw_color=(0, 255, 0),        # colore contorni disegnati (BGR)
    draw_thickness=2               # spessore linea contorno
):
    """
    Elabora un'immagine per rilevare cerchi / oggetti quasi circolari (es. cellule, particelle, bolle, pillole...)

    Flusso principale:
    1. Rimozione illuminazione non uniforme
    2. Miglioramento contrasto locale (CLAHE)
    3. Riduzione rumore preservando bordi (bilateral)
    4. Edge detection robusta (Canny)
    5. Chiusura morfologica per completare cerchi spezzati
    6. Filtraggio contorni per forma (circolarità) e dimensione

    Parametri consigliati per diversi contesti:

    - Cellule al microscopio (luminosità irregolare) → bg_blur_size=81–121, min_area=150–500
    - Pillole / compresse su nastro → bg_blur_size=61–91, canny_low=30, canny_high=100
    - Particelle piccole rumorose → min_area più alto (400–800), min_circularity ≥ 0.75
    - Immagini molto rumorose → bilateral_d=5–7, bilateral_sigma_color/space=40–60
    """
    # -------------------------------------------------------------------------
    # 1. Conversione in scala di grigi
    # -------------------------------------------------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # -------------------------------------------------------------------------
    # 2. Rimozione background / correzione illuminazione non uniforme
    #    (molto importante quando la luce non è omogenea)
    # -------------------------------------------------------------------------
    background = cv2.GaussianBlur(gray, (bg_blur_size, bg_blur_size), 0)
    gray_no_bg = cv2.subtract(gray, background)

    # -------------------------------------------------------------------------
    # 3. Normalizzazione contrasto globale (porta valori tra 0–255)
    # -------------------------------------------------------------------------
    gray_norm = cv2.normalize(gray_no_bg, None, 0, 255, cv2.NORM_MINMAX)

    # -------------------------------------------------------------------------
    # 4. Miglioramento contrasto locale (CLAHE)
    #    → molto utile dopo la sottrazione del background
    # -------------------------------------------------------------------------
    gray_enhanced = apply_clahe_gray(gray_norm)   # assumo tu abbia già questa funzione

    # -------------------------------------------------------------------------
    # 5. Filtro bilaterale → rumore via, bordi preservati
    # -------------------------------------------------------------------------
    blurred = cv2.bilateralFilter(
        gray_enhanced,
        d=bilateral_d,
        sigmaColor=bilateral_sigma_color,
        sigmaSpace=bilateral_sigma_space
    )

    # -------------------------------------------------------------------------
    # 6. Edge detection con Canny
    #    Valori bassi → rileva anche bordi deboli (ma più falsi positivi)
    #    Valori alti  → solo bordi forti (ma può spezzare cerchi)
    # -------------------------------------------------------------------------
    edges = cv2.Canny(blurred, canny_low, canny_high)

    # -------------------------------------------------------------------------
    # 7. Operazione morfologica di chiusura
    #    Serve a collegare bordi interrotti (cerchi incompleti)
    # -------------------------------------------------------------------------
    kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)
    edges_closed = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=morph_iterations
    )

    # -------------------------------------------------------------------------
    # 8. Ricerca contorni (solo esterni – più pulito)
    # -------------------------------------------------------------------------
    contours, _ = cv2.findContours(
        edges_closed,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # -------------------------------------------------------------------------
    # 9. Output + disegno contorni filtrati
    # -------------------------------------------------------------------------
    output = img.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, closed=True)

        if perimeter < 1e-6:  # evita divisione per zero (contorni degeneri)
            continue

        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # ─── Filtro finale ────────────────────────────────────────
        if circularity >= min_circularity and area >= min_area:
            cv2.drawContours(
                output,
                [cnt],
                contourIdx=-1,
                color=draw_color,
                thickness=draw_thickness
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


def play_video_with_contours():

    container = av.open(video_to_analyze_path)
    stream = container.streams.video[0]

    cv2.namedWindow("video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("video", 1400, 800)

    start_perf = time.perf_counter()
    start_time = time.time()

    for frame in container.decode(stream):

        img = frame.to_ndarray(format="bgr24")
        t = float(frame.pts * frame.time_base)

        output = compute_contours(img)

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

    output = compute_contours(img)
    show_frame_img(output)

else:
    print("Errore: frame non estratto")

# play_video_with_contours()