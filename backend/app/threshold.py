import cv2
import av
from PIL import Image

def threshold_test(input_video_path):
    """
    Applica un threshold da 0 a 254 sul frame "medio" (tot. frame / 2) del video
    Output in video/threshold_test
    """

    # open video
    container = av.open(input_video_path)
    stream = container.streams.video[0]

    total_frames = stream.frames
    # if stream.frames returns 0 (not always populated), we can calculate total frames manually
    #total_frames = int(stream.duration * stream.time_base * stream.average_rate)
    middle_frame_idx = total_frames // 2
    container.seek(middle_frame_idx, stream=stream)
    frame = next(container.decode(stream))

    # PyAV -> OpenCV
    frame = frame.to_ndarray(format="bgr24")
    cv2.imwrite(f'video/threshold_test/initial_image.jpg', frame)

    # convert the image to grayscale format
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f'video/threshold_test/initial_image_grayscale.jpg', frame)

    for i in range(255):
        # apply binary thresholding
        ret, thresh = cv2.threshold(img_gray, i, 255, cv2.THRESH_BINARY)

        cv2.imwrite(f'video/threshold_test/image_thres_{i}.jpg', thresh)