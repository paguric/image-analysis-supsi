import os
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog
from app.db import database
from app.dependencies import RoiRepoDep
from app.dependencies import VideoMetadataRepoDep
from app.models.enums import Analisi
from app.services import analysis_service
from app.services import roi_service
from app.services import video_metadata_service

from fastapi import APIRouter


router = APIRouter(prefix="/analysis")


@router.delete("/reset/")
async def reset_db():
    """
    Rimuove il file del db attualmente in uso e ne ricrea uno vuoto.
    """

    # TODO split di questo endpoint in due per rispetto principio Single responsibility:
    #   - Rimozione db
    #   - Creazione nuovo db

    db_path = database.get_db_path()

    # Chiudiamo tutte le vecchie connessioni
    database.reset_engine()

    # Rimozione db vecchio
    if os.path.isfile(db_path):
        os.remove(db_path)
        print(f"{db_path} è stato eliminato con successo")
    else:
        print(f"Nessun db trovato in {db_path}. Non è possibile completare reset")
        # TODO raise Exception

    # Creazione nuovo db vuoto
    database.create_db_and_tables()


@router.get("/diff/results/{min_freq}/{max_freq}/")
def get_diff_csv(
    roi_repo: RoiRepoDep,
    video_metadata_repo: VideoMetadataRepoDep,
    min_freq: int,
    max_freq: int,
):
    """
    Apre finestra dell'OS per selezionare dove salvare il file, genera il CSV della differenza d'intensità per ROI e lo salva su disco.
    """
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        title="Save CSV",
        defaultextension=".csv",
        filetypes=[("CSV files", ".csv"), ("All files", ".*")],
        initialfile="roi_analysis_export.csv",
    )

    root.destroy()

    if not file_path:  # annullato
        return {"success": False, "cancelled": True}

    total_frames = min(
        video_metadata_repo.get(Analisi.PRIMA).total_frames,
        video_metadata_repo.get(Analisi.DOPO).total_frames,
    )
    csv_data = analysis_service.compute_diff_csv(
        roi_repo, min_freq, max_freq, total_frames
    )

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    return {"success": True, "path": file_path, "cancelled": False}


@router.get("/export-csv/diff/frame/{frame}/pixels/")
def export_csv(roi_repo: RoiRepoDep, frame: int):
    """
    Apre finestra dell'OS per selezionare dove salvare il file, genera il CSV della differenza pixel-pixel e lo salva su disco.
    """
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        title="Save CSV",
        defaultextension=".csv",
        filetypes=[("CSV files", ".csv"), ("All files", ".*")],
        initialfile="roi_analysis_export_pixels.csv",
    )

    root.destroy()

    if not file_path:  # annullato
        return {"success": False, "cancelled": True}

    csv_data = np.asarray(analysis_service.compute_diff_csv_pixels(roi_repo, frame))
    np.savetxt(file_path, csv_data, delimiter=",", fmt="%d")

    return {"success": True, "path": file_path, "cancelled": False}
