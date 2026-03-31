import io
import os
import cv2
import numpy as np

from app.routers import roi_controller
from app.services import pipeline_service
from app.services import roi_service
from app.services import cv2_service
from app.models.roi import Roi
from app.models.roi import Analisi
from app.models.video_metadata import VideoMetadata
from app.schemas.pipeline_params import PipelineParams
from app.db.database import SessionDep

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from sqlmodel import select


router = APIRouter(prefix="/pipeline")


@router.post("/")
async def analyze(
    session: SessionDep,
    video_prima: UploadFile = File(...),
    video_dopo: UploadFile = File(...),
):

    prima_bytes = await video_prima.read()
    dopo_bytes = await video_dopo.read()

    output_dir = "../out"
    os.makedirs(output_dir, exist_ok=True)
    prima_avi_path = os.path.join(output_dir, "prima.avi")
    dopo_avi_path = os.path.join(output_dir, "dopo.avi")

    # Salva i file caricati
    with open(prima_avi_path, "wb") as f:
        f.write(prima_bytes)
    with open(dopo_avi_path, "wb") as f:
        f.write(dopo_bytes)

    # Trova il frame più luminoso per le due analisi
    brightest_idx, brightest_frame = cv2_service.brightest_frame(prima_avi_path)
    metadata_prima = VideoMetadata(
        video_path=prima_avi_path, fase=Analisi.PRIMA, brightest_idx=brightest_idx
    )
    metadata_prima.brightest_frame = brightest_frame

    brightest_idx, brightest_frame = cv2_service.brightest_frame(dopo_avi_path)
    metadata_dopo = VideoMetadata(
        video_path=dopo_avi_path, fase=Analisi.PRIMA, brightest_idx=brightest_idx
    )
    metadata_dopo.brightest_frame = brightest_frame

    # Salva frame più luminoso nel db
    session.add(metadata_prima)
    session.add(metadata_dopo)
    session.commit()

    # Estrai le ROI e aggiungi i metadati necessari
    roi_prima: list[Roi] = pipeline_service.extract_rois(metadata_prima.brightest_frame)
    for roi in roi_prima:
        roi.video_path = prima_avi_path
        roi.fase = Analisi.PRIMA

    roi_dopo: list[Roi] = pipeline_service.extract_rois(metadata_dopo.brightest_frame)
    for roi in roi_dopo:
        roi.video_path = dopo_avi_path
        roi.fase = Analisi.DOPO

    # Dopo aver calcolato le ROI, assegna lo stesso indice
    roi_prima, roi_dopo = roi_service.match_rois_by_center(roi_prima, roi_dopo)

    # Salva ROI nel db
    for roi in roi_prima + roi_dopo:
        session.add(roi)
        session.commit()
        session.refresh(roi)


@router.get("/diff/{frame}/")
def get_diff(session: SessionDep, frame: int) -> StreamingResponse:

    roi_prima: list[Roi] = roi_controller.get_roi_list(session, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_controller.get_roi_list(session, Analisi.DOPO)

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    diff = roi_service.compute_aligned_roi_diff(roi_prima, roi_dopo, frame)

    _, buffer = cv2.imencode(".jpg", diff)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.post("/roi/prima/{n}/")
async def analyze_roi_prima(
    session: SessionDep, body: PipelineParams, n: int
) -> StreamingResponse:
    """
    Nota: se una richiesta avesse valori mancanti vengono presi quelli di default definiti nello schema della richiesta PipelineParams
    """
    roi = roi_controller.get_roi_list(session, Analisi.PRIMA)[n]

    # Estrae il frame più luminoso dall'analisi prima
    # TODO spostare questa logica in un VideoController o simili
    statement = select(VideoMetadata).where(VideoMetadata.fase == Analisi.PRIMA)
    video_metadata = session.exec(statement).all()[0]
    brightest_frame: np.ndarray = video_metadata.brightest_frame

    # TODO estrarre da quel frame il patch della ROI con roi.patch
    # TODO applicare la pipeline al patch con pipeline_service.pipeline()
    # TODO creare l'oggetto roi' (la nuova roi) con pipeline_service.find_valid_contours(pipeline[-1])
    # TODO salvare i singoli step della pipeline nel db, in modo però poi da fare una join sull'id della roi e la sua pipeline associata
    # TODO restituire roi': al posto di salvarla in un'altra tabella, gliela facciamo gestire al FE

    _, buffer = cv2.imencode(".jpg", brightest_frame)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.get("/get-number-of-frames")
async def get_number_of_frames(session: SessionDep) -> dict[str, int | float]:
    """
    Restituisce il numero di frame del video prima
    """
    roi_prima: list[Roi] = roi_controller.get_roi_list(session, Analisi.PRIMA)
    video_path = roi_prima[0].video_path

    video_info = cv2_service.get_video_info(video_path)
    frame_count = video_info["total_frames"]
    return {"total_frames": frame_count}
