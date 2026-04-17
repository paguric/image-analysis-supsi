from app.models.video_metadata import VideoMetadata
from app.repositories.video_metadata_repo import VideoMetadataRepository
from app.models.enums import Analisi
import av
import cv2
import numpy as np


def add_video_metadata(repo: VideoMetadataRepository, metadata: VideoMetadata):
    return repo.add(metadata)


def add_video_metadata_from_path(
    repo: VideoMetadataRepository, video_path: str, fase: Analisi
):
    metadata = VideoMetadata(video_path=video_path, fase=fase)

    # Trova il frame più luminoso
    idx, frame = brightest_frame(video_path)
    metadata.brightest_idx = idx
    metadata.brightest_frame = frame

    # Aggiuge altri metadati
    info = get_video_info(video_path)
    metadata.total_frames = info["total_frames"]
    metadata.width = info["width"]
    metadata.height = info["height"]
    metadata.fps = info["fps"]

    return repo.add(metadata)


def get_video_metadata(repo: VideoMetadataRepository, fase: Analisi):
    return repo.get(fase)


def list_video_metadata(repo: VideoMetadataRepository):
    return repo.list()


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


def get_video_info(video_path: str) -> dict[str, int | float]:
    container = av.open(video_path)
    stream = container.streams.video[0]
    frame_count = stream.frames
    width = stream.width
    height = stream.height
    fps = float(stream.average_rate)
    container.close()

    return {"total_frames": frame_count, "width": width, "height": height, "fps": fps}


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
