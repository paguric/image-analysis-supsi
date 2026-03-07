import cv2
from app import cv2_utils
from app import norm

video_to_analyze_path = "video/dopo.avi"


def compute_contours(img):

    gray = norm.clahe(img, 8.5, (6,6))
    gray = norm.min_max_norm(gray)
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




# Trova il frame più luminoso del video
brightest_f, brightness = cv2_utils.brightest_frame(video_to_analyze_path)
print(f"Frame più luminoso: {brightest_f} (brightness: {brightness:.2f})")

# Estrai il frame, calcola i contorni e mostralo
img = cv2_utils.extract_frame(video_to_analyze_path, brightest_f)
if img is not None:
    output = compute_contours(img)
    show_frame_img(output)
else:
    print("Errore: frame non estratto")
