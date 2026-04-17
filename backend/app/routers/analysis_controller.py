import os

from app.db import database
from app.dependencies import RoiRepoDep
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
def get_diff_csv(roi_repo: RoiRepoDep, min_freq: int, max_freq: int):
    """
    Restituisce il file CSV della differenza ROI-ROI.
    """

    # TODO linee duplicate da get_number_of_frames in pipeline_controller. Va aggiunta una colonna a VideoMetadata con il numero di frame, così da sostituire cv2_service
    roi_prima = roi_service.get_roi_list(roi_repo, Analisi.PRIMA)
    roi_dopo = roi_service.get_roi_list(roi_repo, Analisi.DOPO)

    video_path_prima = roi_prima[0].video_path
    video_path_dopo = roi_dopo[0].video_path

    video_prima_info = video_metadata_service.get_video_info(video_path_prima)
    video_dopo_info = video_metadata_service.get_video_info(video_path_dopo)

    total_frames = min(
        video_prima_info["total_frames"], video_dopo_info["total_frames"]
    )

    analysis_service.compute_diff_csv(roi_repo, min_freq, max_freq, total_frames)


# TODO
# @router.get("/diff/results/pixels/")
