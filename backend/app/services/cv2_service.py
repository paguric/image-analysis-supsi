import cv2
import av
import io
import numpy as np
from matplotlib import pyplot as plt


class VideoReader:
    """Context manager per lettura efficiente frame-by-frame."""

    def __init__(self, path: str):
        self.cap = cv2.VideoCapture(path)
        self._opened = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._opened:
            self.cap.release()

    def read(self) -> tuple[bool, np.ndarray | None]:
        return self.cap.read()

    def is_open(self) -> bool:
        return self.cap.isOpened()


def extract_frame(video_path: str, frame_idx: int) -> np.ndarray | None:
    # open video
    container = av.open(video_path)
    stream = container.streams.video[0]

    if frame_idx >= stream.frames or frame_idx < 0:
        return None

    # Calcola il timestamp target (PTS) per il frame richiesto
    target_pts = int((frame_idx / stream.frames) * stream.duration)

    # Salta al keyframe precedente
    container.seek(target_pts, stream=stream)

    # Decodifica finché il timestamp del frame estratto non raggiunge il target
    for av_frame in container.decode(stream):
        if av_frame.pts >= target_pts:
            frame = av_frame.to_ndarray(format="bgr24")
            container.close()
            return frame

    container.close()
    return None


def brightest_frame(video_path: str) -> tuple[int, np.ndarray]:
    """
    Trova il frame più luminoso
    """

    brightest_frame = None
    brightest_idx = -1
    max_brightness = -1

    with VideoReader(video_path) as cap1:
        for i in range(get_video_info(video_path)["total_frames"]):
            ret, frame = cap1.read()
            if not ret:
                break

            # convert the image to grayscale format
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # calculate mean brightness of the frame
            brightness = img_gray.mean()

            if brightness > max_brightness:
                brightest_idx = i
                brightest_frame = frame
                max_brightness = brightness

    return brightest_idx, brightest_frame


def get_video_info(video_path: str) -> dict[str, int | float]:
    container = av.open(video_path)
    stream = container.streams.video[0]
    frame_count = stream.frames
    width = stream.width
    height = stream.height
    fps = float(stream.average_rate)
    container.close()

    return {"total_frames": frame_count, "width": width, "height": height, "fps": fps}


def plot_histogram(
    frame: np.ndarray, log_scale: bool = False, normalized: bool = False
):
    """
    -> Attualmente inutilizzata
    Mostra il frame e a fianco il suo relativo istogramma con Matplotlib
    È possibile attivare la visualizzazione in scala logaritmica e/o con valori normalizzati (da 0.0 a 1.0)
    src: https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html
    chat: https://claude.ai/share/8b8adb6e-83a1-49a0-8dbd-51e286991413
    """
    assert frame is not None, "frame could not be read"

    img = frame.astype(np.float32) / 255.0 if normalized else frame
    x_range = [0, 1] if normalized else [0, 256]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Show image
    ax1.imshow(img, cmap="gray", vmin=0, vmax=1)
    ax1.set_title("Image")
    ax1.axis("off")

    # Show histogram
    ax2.hist(img.ravel(), 256, x_range)
    if log_scale:
        ax2.set_yscale("log")
    ax2.set_title("Histogram")
    ax2.set_xlabel("Intensity")
    ax2.set_ylabel("Pixel Count")

    # plt.yscale('log')
    plt.tight_layout()
    plt.show()


def time_convert(seconds):
    """
    -> Attualmente inutilizzata
    """
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"
