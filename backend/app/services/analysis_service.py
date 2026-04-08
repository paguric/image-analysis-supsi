import csv

from app.dependencies import RoiRepoDep
from app.models.roi import Roi
from app.models.roi import Analisi


def compute_diff_csv(
    roi_repo: RoiRepoDep, min_freq: int, max_freq: int, total_frames: int
):
    rois = roi_repo.list_all()
    freq_increment = (max_freq - min_freq) / total_frames
    data = []

    # Creazione intestazione
    row = []
    for i in range(total_frames):
        row.append(f"FREQ_{min_freq + freq_increment * (i + 1)}")
    data.append(row)

    for i in range(len(rois) // 2):
        roi_prima = roi_repo.get(i, Analisi.PRIMA)
        roi_dopo = roi_repo.get(i, Analisi.DOPO)

        row = [f"ROI_{i}"]

        for j in range(total_frames):
            intensity_prima, _, _, _ = roi_prima.get_intensity(j)
            intensity_dopo, _, _, _ = roi_dopo.get_intensity(j)

            row.append(intensity_dopo - intensity_prima)

        data.append(row)

    # Conversione in CSV
    with open("out/temp.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
