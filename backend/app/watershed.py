import cv2
import av
import numpy as np
import os
from app import cv2_utils

def watershed_test(img: np.ndarray, threshold: int) -> np.ndarray | None:
    """
    Applica watershed sull'immagine
    Output in out/watershed_test
    src: https://docs.opencv.org/4.x/d3/db4/tutorial_py_watershed.html
    chat: https://claude.ai/share/431e4b0b-53b2-494f-8c1c-1890db47d846
    """
    os.makedirs('out/watershed_test', exist_ok=True)

    # If image is grayscale, convert to BGR
    # cv2.watershed (at the end of this function) requires a 3-channel image
    if len(img.shape) == 2 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    # convert the image to grayscale format
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ATTENZIONE - qua ho inserito un valore manualmente dopo vari test. Non è ideale ecco...
    ret, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    # DEBUG
    cv2.imwrite(f'out/watershed_test/step_1.jpg', thresh)

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    # DEBUG
    cv2.imwrite(f'out/watershed_test/step_2.jpg', sure_bg)
    cv2.imwrite(f'out/watershed_test/step_3.jpg', sure_fg)
    
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    markers = cv2.watershed(img,markers)
    img[markers == -1] = [255,0,0]

    # DEBUG
    cv2.imwrite(f'out/watershed_test/step_4.jpg', img)
    return img
