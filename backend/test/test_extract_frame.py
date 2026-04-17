import pytest
import numpy as np
import av
from app.services import video_metadata_service


@pytest.fixture
def video_test(tmp_path):
    percorso = str(tmp_path / "test.mp4")

    container = av.open(percorso, mode="w")
    stream = container.add_stream("h264", rate=1)
    stream.width = 10
    stream.height = 10
    stream.pix_fmt = "yuv420p"

    # Frame 0: scuro
    frame_scuro = av.VideoFrame.from_ndarray(
        np.zeros((10, 10, 3), dtype=np.uint8), format="rgb24"
    )
    frame_scuro.pts = 0
    for packet in stream.encode(frame_scuro):
        container.mux(packet)

    # Frame 1: chiaro
    frame_chiaro = av.VideoFrame.from_ndarray(
        np.full((10, 10, 3), 255, dtype=np.uint8), format="rgb24"
    )
    frame_chiaro.pts = 1
    for packet in stream.encode(frame_chiaro):
        container.mux(packet)

    # Flush
    for packet in stream.encode():
        container.mux(packet)

    container.close()
    return percorso


def test_extract_frame_valido(video_test):
    frame = video_metadata_service.extract_frame(video_test, 1)
    assert frame is not None
    assert frame.shape == (10, 10, 3)
    assert np.mean(frame) > 200.0


def test_extract_frame_primo(video_test):
    frame = video_metadata_service.extract_frame(video_test, 0)
    assert frame is not None
    assert np.mean(frame) < 50.0  # deve essere scuro


def test_extract_frame_fuori_range(video_test):
    frame = video_metadata_service.extract_frame(video_test, 99)
    assert frame is None


def test_extract_frame_negativo(video_test):
    frame = video_metadata_service.extract_frame(video_test, -1)
    assert frame is None


def test_get_video_info(video_test):
    info = video_metadata_service.get_video_info(video_test)

    # Il video ha 2 frame
    assert info["total_frames"] == 2
    assert info["width"] == 10
    assert info["height"] == 10
    assert info["fps"] == 1.0


def test_frame_indexing(video_test):
    """
    Verifica che i frame siano 0-based:
    - frame 0 = primo frame (scuro)
    - frame 1 = secondo frame (chiaro)
    - total_frames = 2, quindi l'ultimo frame valido è all'indice 1
    """
    info = video_metadata_service.get_video_info(video_test)
    total = info["total_frames"]  # 2

    # L'indice va da 0 a total_frames-1
    primo = video_metadata_service.extract_frame(video_test, 0)
    ultimo = video_metadata_service.extract_frame(video_test, total - 1)
    fuori = video_metadata_service.extract_frame(video_test, total)  # non esiste

    assert primo is not None
    assert np.mean(primo) < 50.0  # frame 0 = scuro

    assert ultimo is not None
    assert np.mean(ultimo) > 200.0  # frame 1 = chiaro

    assert fuori is None  # total_frames non è un indice valido
