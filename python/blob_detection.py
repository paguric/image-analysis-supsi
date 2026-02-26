import cv2
import av
import time
# import io
# import numpy as np
# import aspose.pycore as aspycore



# ============================================================
# FUNZIONE: aumento contrasto con Aspose (input/output OpenCV)
# ============================================================

# def increase_brightness(img, contrast=10):
#     """
#     img: immagine OpenCV BGR (numpy array)
#     contrast: valore di contrasto Aspose
#     return: immagine OpenCV BGR
#     """

#     # OpenCV -> TIFF in memoria
#     success, encoded = cv2.imencode(".tiff", img)
#     if not success:
#         raise RuntimeError("Errore encoding immagine")

#     input_stream = io.BytesIO(encoded.tobytes())

#     # Aspose Imaging
#     with Image.load(input_stream) as image:
#         raster = aspycore.as_of(image, RasterImage)

#         if not raster.is_cached:
#             raster.cache_data()

#         raster.adjust_contrast(contrast)

#         output_stream = io.BytesIO()
#         options = TiffOptions(TiffExpectedFormat.DEFAULT)
#         options.bits_per_sample = [8, 8, 8]
#         options.photometric = TiffPhotometrics.RGB

#         raster.save(output_stream, options)

#     # TIFF -> OpenCV
#     output_stream.seek(0)
#     file_bytes = np.frombuffer(output_stream.read(), np.uint8)
#     img_out = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#     return img_out


# ============================================================
# APERTURA VIDEO
# ============================================================

container = av.open("video\\dopo.avi")
stream = container.streams.video[0]

start = time.perf_counter()
cv2.namedWindow("video", cv2.WINDOW_NORMAL)
cv2.resizeWindow("video", 1400, 800)


# ============================================================
# CONFIGURAZIONE SIMPLE BLOB DETECTOR
# ============================================================

params = cv2.SimpleBlobDetector_Params()

# Threshold
params.minThreshold = 5
params.maxThreshold = 255

# Area
params.filterByArea = True
params.minArea = 100
params.maxArea = 5000

# Colore blob
params.filterByColor = True
params.blobColor = 0  # blob scuri

# Filtri geometrici (disattivati)
params.filterByCircularity = False
params.filterByConvexity = False
params.filterByInertia = False

detector = cv2.SimpleBlobDetector_create(params)


# ============================================================
# LOOP PRINCIPALE
# ============================================================

for frame in container.decode(stream):

    # PyAV -> OpenCV
    img = frame.to_ndarray(format="bgr24")

    # Aumento contrasto globale (Aspose)
    # img = increase_brightness(img, contrast=10)

    # Timestamp reale del frame
    t = float(frame.pts * frame.time_base)

    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    gray = clahe.apply(gray)

    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Blob detection
    keypoints = detector.detect(gray)

    # Disegno blob
    im_with_keypoints = cv2.drawKeypoints(
        img,
        keypoints,
        None,
        (0, 0, 255),
        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )

    # Sync tempo reale
    while time.perf_counter() - start < t:
        time.sleep(0.001)

    # Visualizzazione
    cv2.imshow("video", im_with_keypoints)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ============================================================
# CLEANUP
# ============================================================

cv2.destroyAllWindows()