import av
import cv2
import time
import numpy as np

# ------------------------------
# Global variables
# ------------------------------
prev_fused = None  # per temporal smoothing

# ------------------------------
# Utility Functions
# ------------------------------
def resize_frame(frame, width, height):
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

def to_grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)



def apply_clahe(gray):
    # se aumento cliplimit = più contrasto, più rischio di amplificare rumore
    # se diminuisco cliplimit = contrasto più naturale
    # se aumento tileGridSize = contrasto più uniforme ma bordi locali meno evidenti
    # se diminuisco tileGridSize = più dettagli locali (utile se illuminazione molto irregolare)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(64, 64))
    return clahe.apply(gray)

def bilateral_smooth(gray):
    # parametri (oltre a gray): d (Diametro del kernel per ogni pixel), 
    # sigmaColor (Quanto i colori vicini influenzano la media)
    # e sigmaSpace (Quanto pixel lontani influenzano)

    # se aumento d = più smoothing ma bordi più sfocati
    # se diminuisco d = meno smoothing, più dettagli e rumore
    # se aumento sigmaColor = più smoothing su valori simili (utile se rumore forte)
    # se diminuisco sigmaColor = mantiene più dettagli, meno smoothing
    # se aumento sigmaSpace = smoothing più esteso spazialmente
    # se diminuisco sigmaSpace = solo pixel vicini contano
    return cv2.bilateralFilter(gray, 8, 90, 90)



def dynamic_canny(gray):
    sigma = np.std(gray)
    lower = max(20, int(0.66 * sigma))
    upper = min(200, int(1.33 * sigma))
    return cv2.Canny(gray, lower, upper)

def laplacian_edge(gray):
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return cv2.convertScaleAbs(lap)

def sobel_gradient(gray):
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    mag = np.sqrt(sobelx**2 + sobely**2)
    return cv2.convertScaleAbs(mag)

def fuse_edges(canny, lap, sobel):
    fused = cv2.addWeighted(canny, 0.6, lap, 0.3, 0)
    fused = cv2.addWeighted(fused, 0.7, sobel, 0.3, 0)
    return fused

def morphology_close(fused):
    kernel = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(fused, cv2.MORPH_CLOSE, kernel)

def temporal_smooth(fused):
    global prev_fused
    if prev_fused is None:
        prev_fused = fused.copy()
    fused_smoothed = cv2.addWeighted(fused, 0.7, prev_fused, 0.3, 0)
    prev_fused = fused_smoothed.copy()
    return fused_smoothed

def overlay_edges(frame, fused):
    overlay = frame.copy()
    overlay[fused > 40] = [0, 0, 255]  # rosso sui bordi
    return overlay

# ------------------------------
# Frame processing
# ------------------------------
def process_frame(img):
    gray = to_grayscale(img)
    clahe_gray = apply_clahe(gray)
    smooth = bilateral_smooth(clahe_gray)
    canny = dynamic_canny(smooth)
    lap = laplacian_edge(smooth)
    sobel = sobel_gradient(smooth)
    fused = fuse_edges(canny, lap, sobel)
    fused = morphology_close(fused)
    fused = temporal_smooth(fused)
    output = overlay_edges(img, fused)
    return output

# ------------------------------
# Main computation
# ------------------------------


def compute_roi(video_path):
    container = av.open(video_path)
    stream = container.streams.video[0]

    # timing reale
    start = time.perf_counter()

    # finestra per display
    cv2.namedWindow("video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("video", 1400, 800)



    # VideoWriter (scommentare per esportare un video)
    # prima decodifica per dimensioni e FPS

    # first_frame = next(container.decode(stream))
    # height, width = first_frame.height, first_frame.width
    # fps = float(stream.average_rate)
    # fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # out = cv2.VideoWriter("video/post_detection.avi", fourcc, fps, (width, height))
    # img = first_frame.to_ndarray(format="bgr24")
    # output = process_frame(img)
    # cv2.imshow("video", output)
    # cv2.waitKey(1)
    



    # loop su tutti gli altri frame
    for frame in container.decode(stream):
        img = frame.to_ndarray(format="bgr24")
        # out.write(output)    


        # tempo reale del frame
        t = float(frame.pts * frame.time_base)

        # ---- CV ----
        process_frame(img)
        

        # sincronizzazione vera
        while time.perf_counter() - start < t:
            time.sleep(0.001)

        # mostrare il frame processato
        cv2.imshow("video", img)
        break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # pulizia
    #out.release()
    cv2.destroyAllWindows()
    container.close()