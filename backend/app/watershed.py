import cv2
import av
import numpy as np
import os
from app import preprocessing

def watershed_test(input_video_path: str, i: int):
    """
    Applica watershed sul frame iesimo
    Output in out/watershed_test
    src: https://docs.opencv.org/4.x/d3/db4/tutorial_py_watershed.html
    """
    os.makedirs('out/watershed_test', exist_ok=True)

    # open video
    container = av.open(input_video_path)
    stream = container.streams.video[0]

    frame = preprocessing.extract_frame(input_video_path, i)

    # convert the image to grayscale format
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # find an approximate estimate of the ROIs with Otsu's binarization
    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    cv2.imwrite(f'out/watershed_test/step_1.jpg', thresh)
