import cv2
import av
import numpy as np
import os
from PIL import Image
from app import cv2_utils

def threshold_test(input_video_path):
    """
    Applica un threshold da 0 a 254 sul frame "medio" (tot. frame / 2) del video
    Output in video/threshold_test
    """
    os.makedirs('video/threshold_test', exist_ok=True)

    # open video
    container = av.open(input_video_path)
    stream = container.streams.video[0]
    total_frames = stream.frames
    # if stream.frames returns 0 (not always populated), we can calculate total frames manually
    #total_frames = int(stream.duration * stream.time_base * stream.average_rate)
    middle_frame_idx = total_frames // 2

    frame = cv2_utils.extract_frame(input_video_path, middle_frame_idx)
    cv2.imwrite(f'video/threshold_test/initial_image.jpg', frame)

    # convert the image to grayscale format
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f'video/threshold_test/initial_image_grayscale.jpg', img_gray)

    for i in range(255):
        # apply binary thresholding
        ret, thresh = cv2.threshold(img_gray, i, 255, cv2.THRESH_BINARY)

        cv2.imwrite(f'video/threshold_test/image_thres_{i}.jpg', thresh)


def brightness_test(input_video_path):
    """
    Applica valori di luminosità da -127 a +127 sul frame medio del video.
    beta in convertScaleAbs aggiunge un offset costante a ogni pixel:
      - beta < 0 → immagine più scura
      - beta > 0 → immagine più chiara
    alpha=1 mantiene il contrasto invariato.
    Output in video/brightness_test
    """
    os.makedirs('video/brightness_test', exist_ok=True)

    container = av.open(input_video_path)
    stream = container.streams.video[0]
    total_frames = stream.frames
    middle_frame_idx = total_frames // 2

    frame = cv2_utils.extract_frame(input_video_path, middle_frame_idx)
    cv2.imwrite('video/brightness_test/initial_image.jpg', frame)

    for i in range(-127, 128):  # da -127 a +127 inclusi
        bright = cv2.convertScaleAbs(frame, alpha=1, beta=i)
        cv2.imwrite(f'video/brightness_test/image_bright_{i}.jpg', bright)


def contrast_test(input_video_path):
    """
    Applica valori di contrasto da 0.0 a 3.0 (step 0.01) sul frame medio del video.
    alpha in convertScaleAbs moltiplica ogni pixel:
      - alpha < 1 → contrasto ridotto (immagine più "piatta")
      - alpha = 1 → invariato
      - alpha > 1 → contrasto aumentato (immagine più "netta/vivida")
    beta=0 mantiene la luminosità invariata.
    Output in video/contrast_test
    """
    os.makedirs('video/contrast_test', exist_ok=True)

    container = av.open(input_video_path)
    stream = container.streams.video[0]
    total_frames = stream.frames
    middle_frame_idx = total_frames // 2

    frame = cv2_utils.extract_frame(input_video_path, middle_frame_idx)
    cv2.imwrite('video/contrast_test/initial_image.jpg', frame)

    # np.arange con float: da 0.0 a 3.0 con step 0.01 → 301 valori
    for alpha in np.arange(0.0, 3.01, 0.01):
        contrasted = cv2.convertScaleAbs(frame, alpha=alpha, beta=0)
        # sostituiamo il punto con underscore nel nome file
        alpha_str = f"{alpha:.2f}".replace('.', '_')
        cv2.imwrite(f'video/contrast_test/image_contrast_{alpha_str}.jpg', contrasted)