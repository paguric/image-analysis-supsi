import cv2
import numpy as np

VIDEO_PATH = "../video/prima.avi"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"[ERRORE] Impossibile aprire il video: {VIDEO_PATH}")
    exit(1)

SCREEN_W = 1920
SCREEN_H = 1080

# ── Oggetti creati una volta sola fuori dal loop ──────────────────────────────
# CLAHE: migliora contrasto locale su immagini scure
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
# Kernel morfologico per la dilatazione
kernel = np.ones((5, 5), np.uint8)
# ─────────────────────────────────────────────────────────────────────────────

def empty(a):
    pass

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 240)
cv2.createTrackbar("threshold1", "Parameters", 38, 255, empty)
cv2.createTrackbar("threshold2", "Parameters", 31, 255, empty)
cv2.createTrackbar("Area",       "Parameters", 5000, 30000, empty)


def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width  = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(rows):
            for y in range(cols):
                target_shape = (imgArray[0][0].shape[1], imgArray[0][0].shape[0])
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], target_shape, None, scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        hor = [np.hstack(imgArray[x]) for x in range(rows)]
        ver = np.vstack(hor)
    else:
        for x in range(rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        ver = np.hstack(imgArray)
    return ver


def getContours(img, imgContour):
    # CHAIN_APPROX_SIMPLE: meno punti memorizzati rispetto a CHAIN_APPROX_NONE
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areaMin = cv2.getTrackbarPos("Area", "Parameters")  # letto una volta per tutti i contorni
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > areaMin:
            cv2.drawContours(imgContour, contours, -1, (255, 0, 255), 7)
            peri   = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            print(len(approx))
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(imgContour, "Points:" + str(len(approx)), (x+w+20, y+20),  cv2.FONT_HERSHEY_COMPLEX, .7,  (0, 255, 0), 2)
            cv2.putText(imgContour, "Area:"   + str(int(area)),   (x+w+20, y+45),  cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)


# Calcola lo scale una volta dal primo frame
ret, first = cap.read()
if not ret:
    print("[ERRORE] Impossibile leggere il primo frame")
    exit(1)
scale = round(min(SCREEN_W / (first.shape[1] * 3), SCREEN_H / (first.shape[0] * 2)), 2)
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # riavvolgi


while True:
    success, img = cap.read()

    # Fine video: ricomincia dall'inizio
    if not success:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    imgContour = img.copy()

    # Preprocessing
    # bilateralFilter: riduce rumore preservando i bordi meglio del GaussianBlur
    imgBlur = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    imgGray = clahe.apply(imgGray)

    threshold1 = cv2.getTrackbarPos("threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
    imgDil   = cv2.dilate(imgCanny, kernel, iterations=1)

    getContours(imgDil, imgContour)

    imgStack = stackImages(scale, ([img, imgBlur, imgGray], [imgCanny, imgContour, imgDil]))
    cv2.imshow("Result", imgStack)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()