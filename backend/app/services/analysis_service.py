import csv

from app.dependencies import RoiRepoDep
from app.models.roi import Roi
from app.models.roi import Analisi


def compute_diff_csv(
    roi_repo: RoiRepoDep, min_freq: int, max_freq: int, total_frames: int
):
    roi_prima = roi_repo.list(Analisi.PRIMA)
    roi_dopo = roi_repo.list(Analisi.DOPO)
    freq_increment = (max_freq - min_freq) / total_frames
    data = []

    # Creazione intestazione
    row = []
    row.append("")  # colonna vuota
    for i in range(total_frames):
        row.append(f"FREQ_{min_freq + freq_increment * (i + 1)}")
    data.append(row)

    for i in range(len(roi_prima)):
        row = [f"ROI_{i}"]

        for j in range(total_frames):
            _, intensity_prima, _, _ = roi_prima[i].get_intensity(j)
            _, intensity_dopo, _, _ = roi_dopo[i].get_intensity(j)

            row.append(intensity_dopo - intensity_prima)

        data.append(row)

    # Conversione in CSV
    with open("out/temp.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
