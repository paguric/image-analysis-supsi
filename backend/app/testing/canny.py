import cv2
import av
import time
import numpy as np

video_to_analyze_path = "../../video/dopo.avi"


def time_convert(seconds):
    """Converte secondi in formato mm:ss"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"


def apply_clahe_gray(img):
    """Aumenta contrasto locale e luminosità su un'immagine grayscale"""
    # aumento contrasto locale
    clahe = cv2.createCLAHE(clipLimit=8.5, tileGridSize=(6, 6))
    return clahe.apply(img)




def brightest_frame(video_path: str) -> tuple[int, float]:
    """
    Scorre tutti i frame del video e restituisce
    l'indice e la luminosità del frame più luminoso
    """
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
    """
    Estrae un singolo frame dal video dato il suo indice.
    Restituisce il frame come array BGR, o None se fallisce.
    """
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




def compute_contours(img):
    """
    Data un'immagine BGR:
    1. Converte in grayscale
    2. Aumenta il contrasto con CLAHE
    3. Riduce il rumore con Gaussian Blur
    4. Rileva i bordi con Canny
    5. Trova e disegna i contorni sull'immagine originale
    Restituisce l'immagine BGR con i contorni sovrapposti
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = apply_clahe_gray(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blur, threshold1=1, threshold2=133)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    output = img.copy()
    cv2.drawContours(output, contours, -1, (0, 255, 0), 2)
    return output




def show_frame_img(img):
    """Mostra un'immagine in una finestra ridimensionabile, chiudi con 'q'"""
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img", 1400, 800)
    cv2.imshow("img", img)

    while True:
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def play_video_with_contours():
    """
    Riproduce il video in realtime applicando
    il rilevamento dei contorni ad ogni frame
    """
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

        # Sync con il tempo reale del video
        while time.perf_counter() - start_perf < t:
            time.sleep(0.001)

        cv2.imshow("video", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Durata video:", time_convert(time.time() - start_time))
    cv2.destroyAllWindows()
    container.close()




# Trova il frame più luminoso del video
brightest_f, brightness = brightest_frame(video_to_analyze_path)
print(f"Frame più luminoso: {brightest_f} (brightness: {brightness:.2f})")

# Estrai il frame, calcola i contorni e mostralo
img = extract_frame(video_to_analyze_path, brightest_f)
if img is not None:
    output = compute_contours(img)
    show_frame_img(output)
else:
    print("Errore: frame non estratto")

# Riproduce l'intero video con i contorni in realtime
# play_video_with_contours()