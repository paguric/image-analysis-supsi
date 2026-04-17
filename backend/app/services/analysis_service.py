import csv

from app.dependencies import RoiRepoDep
from app.models.enums import Analisi
from app.services.video_metadata_service import VideoReader


def compute_diff_csv(
    roi_repo: RoiRepoDep, min_freq: int, max_freq: int, total_frames: int
):
    roi_prima = roi_repo.list(Analisi.PRIMA)
    roi_dopo = roi_repo.list(Analisi.DOPO)
    freq_increment = (max_freq - min_freq) / total_frames

    # Intestazione
    header = [""] + [
        f"FREQ_{min_freq + freq_increment * (i + 1)}" for i in range(total_frames)
    ]

    # Inizializza una riga per ogni ROI
    data = [header] + [[f"ROI_{i}"] for i in range(len(roi_prima))]

    reader_prima = VideoReader(roi_prima[0].video_path)
    reader_dopo = VideoReader(roi_dopo[0].video_path)

    # Loop principale: un frame alla volta, tutte le ROI
    for j in range(total_frames):
        _, frame_prima = reader_prima.read()
        _, frame_dopo = reader_dopo.read()

        if frame_prima is None or frame_dopo is None:
            raise ValueError(f"Frame None al frame {j}")

        for i in range(len(roi_prima)):
            patch_prima = roi_prima[i].get_pixels_from_frame(frame_prima)
            patch_dopo = roi_dopo[i].get_pixels_from_frame(frame_dopo)

            intensity_prima, _, _, _ = roi_prima[i].get_intensity_from_patch(
                patch_prima
            )
            intensity_dopo, _, _, _ = roi_dopo[i].get_intensity_from_patch(patch_dopo)

            data[i + 1].append(intensity_dopo - intensity_prima)

    with open("out/temp.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
