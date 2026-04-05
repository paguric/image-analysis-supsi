import pytest
import numpy as np
import cv2

from backend.app.services import cv2_service


def test_example():

    assert 1+1 == 2




# def test_time_convert():
#     assert cv2_service.time_convert(0) == "0:00"
#     assert cv2_service.time_convert(65) == "1:05"
#     assert cv2_service.time_convert(3600) == "60:00"


# def test_plot_histogram(mocker):
#     mocker.patch("matplotlib.pyplot.show")
#     frame_test = np.zeros((10, 10), dtype=np.uint8)

#     cv2_service.plot_histogram(frame_test)

#     import matplotlib.pyplot as plt

#     plt.show.assert_called_once()


# # simile al foreach
# @pytest.fixture
# def video_test(tmp_path):
#     percorso = str(tmp_path / "test.mp4")
#     # Parametri: percorso, CODED, numero di frames e dimensioni
#     out = cv2.VideoWriter(percorso, cv2.VideoWriter_fourcc(*"mp4v"), 1, (10, 10))

#     frame_scuro = np.zeros((10, 10, 3), dtype=np.uint8)
#     frame_chiaro = np.full((10, 10, 3), 255, dtype=np.uint8)

#     out.write(frame_scuro)
#     out.write(frame_chiaro)
#     out.release()

#     return percorso


# def test_brightest_frame(video_test):
#     indice, luminosita = cv2_service.brightest_frame(video_test)

#     assert indice == 1
#     assert luminosita > 200.0


# def test_extract_frame_valido(video_test):
#     frame = cv2_service.extract_frame(video_test, 1)

#     assert frame is not None
#     assert frame.shape == (10, 10, 3)
#     assert np.mean(frame) > 200.0


# def test_extract_frame_fuori_limite(video_test):
#     frame = cv2_service.extract_frame(video_test, 999)

#     assert frame is None
