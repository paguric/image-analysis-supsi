import cv2
import av
import time
import numpy as np
#from matplotlib import pyplot as plt

def simple_canny_test(video_path: str,) -> np.ndarray | None:
    """
    Applica canny sul frame "medio" (tot. frame / 2) del video
    con valori di T_lower e T_upper da 50 a 150
    Output in video/simple_canny_test
    """

    edges = cv2.Canny(img,100,200)

    return 1

def time_convert(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"

def canny_contour_detection(video_to_analyze_path):

    # Apertura video
    container = av.open(video_to_analyze_path)
    stream = container.streams.video[0]

    start_perf = time.perf_counter()
    start_time = time.time()

    cv2.namedWindow("video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("video", 1400, 800)

    # Riproduzione frame-by-frame
    for frame in container.decode(stream):

        # PyAV → OpenCV
        img = frame.to_ndarray(format="bgr24")

        # timestamp reale del frame
        t = float(frame.pts * frame.time_base)

        # PREPROCESSING
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # aumento contrasto locale
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # riduzione rumore
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # CANNY EDGE DETECTION
        edges = cv2.Canny(
            blur,
            threshold1=50,
            threshold2=150
        )

        # CONTORNI
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # disegno contorni
        output = img.copy()
        cv2.drawContours(output, contours, -1, (0, 255, 0), 2)

        # Sync realtime
        while time.perf_counter() - start_perf < t:
            time.sleep(0.001)

        cv2.imshow("video", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    end_time = time.time()
    print("Durata video:", time_convert(end_time - start_time))

    cv2.destroyAllWindows()