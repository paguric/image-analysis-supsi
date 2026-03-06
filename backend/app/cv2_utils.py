import cv2
import av
import numpy as np
from matplotlib import pyplot as plt

def extract_frame(video_path: str, frame_idx: int) -> np.ndarray | None:
    """
    Extracts a single frame from a video by index.
    Returns the frame as a BGR numpy array, or None if extraction fails.
    """

    # open video
    container = av.open(video_path)
    stream = container.streams.video[0]

    if frame_idx >= stream.frames or frame_idx < 0:
        return None

    container.seek(frame_idx, stream=stream)
    av_frame = next(container.decode(stream))

    # PyAV -> OpenCV
    frame = av_frame.to_ndarray(format="bgr24")
    
    return frame


def brightest_frame(video_path: str) -> tuple[int, float]:
    """
    Trova l'indice e la luminositò del frame più luminoso
    """

    brightest_index = 0
    max_brightness = -1
    
    # open video
    container = av.open(video_path)
    stream = container.streams.video[0]

    for i, frame in enumerate(container.decode(stream)):
        # PyAV -> OpenCV
        frame = frame.to_ndarray(format="bgr24")
        # convert the image to grayscale format
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate mean brightness of the frame
        brightness = img_gray.mean()

        if brightness > max_brightness:
            max_brightness = brightness
            brightest_index = i

    container.close()
    return brightest_index, max_brightness


def plot_histogram(frame: np.ndarray):
    """
    Mostra il frame e il suo relativo istogramma con Matplotlib
    """
    assert frame is not None, "frame could not be read"
    plt.hist(frame.ravel(),256,[0,256]); plt.show()
