import cv2
import av
import numpy as np

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
