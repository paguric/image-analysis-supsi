import cv2
import av
import time
from PIL import Image

"""
# Convertitore 
def time_convert(seconds):
    mins = seconds // 60
    secs = seconds % 60
    print(f"Time Lapsed = {int(mins)}:{int(secs):02d}")

# Apertura video
container = av.open("video/video_test.mp4")
stream = container.streams.video[0]

start = time.perf_counter()
cv2.namedWindow("video", cv2.WINDOW_NORMAL)
cv2.resizeWindow("video", 1400, 800)


start_time = time.time()

# Riproduzione Video
for frame in container.decode(stream):

    # PyAV -> OpenCV
    img = frame.to_ndarray(format="bgr24")

    # Timestamp reale del frame
    t = float(frame.pts * frame.time_base)

    # convert the image to grayscale format
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply binary thresholding
    ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

                                      
    # draw contours on the original image
    image_copy = img.copy()
    cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    # Sync tempo reale
    while time.perf_counter() - start < t:
        time.sleep(0.001)

    # Visualizzazione
    cv2.imshow("video", image_copy)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

end_time = time.time()

print(f"Tempo durata video: {time_convert(end_time - start_time)}")

cv2.destroyAllWindows()
"""