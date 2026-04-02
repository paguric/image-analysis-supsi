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
from app.models.diff import Diff
from app.models.pipeline import Pipeline
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
    """
    Estrae le ROI dai video delle due analisi e le salva nel db.
    """

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
    """
    Calcola il frame differenziale fra le due analisi e lo salva nel db.
    """
    
    # Se il differenziale è già stato calcolato ed è nel db, lo possiamo restituire subito
    # TODO spostare questa query (come quella in analyze_roi_prima) in un metodo a parte
    result: Diff | None = session.exec(
        select(Diff).where(Diff.frame == frame)
    ).all()

    if len(result) != 0:
        diff : Diff = result[0]
        # TODO impacchettare queste tre righe per creare l'output in un metodo a parte
        _, buffer = cv2.imencode(".jpg", diff.diff_frame)
        io_buffer = io.BytesIO(buffer)

        return StreamingResponse(io_buffer, media_type="image/jpeg")

    roi_prima: list[Roi] = roi_controller.get_roi_list(session, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_controller.get_roi_list(session, Analisi.DOPO)

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")
    
    diff_frame : np.ndarray = roi_service.compute_aligned_roi_diff(roi_prima, roi_dopo, frame)

    # Calcola e salva il differenziale
    diff = Diff(frame=frame)
    diff.diff_frame = diff_frame
    session.add(diff)
    session.commit()
    session.refresh(diff)

    _, buffer = cv2.imencode(".jpg", diff.diff_frame)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.get("/diff/{frame}/contours/")
def get_diff(session: SessionDep, frame: int) -> StreamingResponse:
    """
    Applica un overlay che permette di identificare le ROI sul differenziale fra le due analisi.
    L'overlay è calcolato come il minEnclosingCircle di raggio minimo fra le due patch.
    """
    
    # TODO


@router.post("/roi/prima/{n}/")
async def analyze_roi_prima(session: SessionDep, body: PipelineParams, n: int):
    """
    Restituisce la nuova ROI identificati dall'applicazione della pipeline sulla singola patch.
    Nota: se nel body della richiesta ci fossero valori mancanti vengono presi quelli di default definiti nello schema della richiesta PipelineParams.
    """
    roi = roi_controller.get_roi_list(session, Analisi.PRIMA)[n]

    # Estrae il frame più luminoso dall'analisi prima
    # TODO spostare questa logica in un VideoController o simili
    statement = select(VideoMetadata).where(VideoMetadata.fase == Analisi.PRIMA)
    video_metadata = session.exec(statement).all()[0]

    patch = roi.get_pixels(video_metadata.brightest_idx)

    # Applica la pipeline al patch
    pipeline_steps: list[np.ndarray] = pipeline_service.pipeline(patch, body)
    roi_new = pipeline_service.find_valid_contours(pipeline_steps[-1], body)

    # Salva i singoli step della pipeline nel db
    new_pipeline = Pipeline(roi_id=roi.id)
    new_pipeline.hpf = pipeline_steps[0]
    new_pipeline.enhanced = pipeline_steps[1]
    new_pipeline.edges = pipeline_steps[2]
    new_pipeline.edges_closed = pipeline_steps[3]

    session.add(new_pipeline)
    session.commit()
    session.refresh(new_pipeline)

    # TODO definire Pydantic/SQLModel schema di risposta (aggiungerlo anche alla firma del metodo!)
    # return roi_new
    return None


@router.get("/roi/prima/{i}/step/{j}")
async def get_step_pipeline_roi_prima(
    session: SessionDep,
    i: int,
    j: int,
) -> StreamingResponse:
    """
    Restituisce gli step intermedi dell'applicazione della pipeline su una singola ROI.
    """
    roi = roi_controller.get_roi_list(session, Analisi.PRIMA)[i]

    # TODO spostare questa query (e tutte le altre) in un metodo a parte
    pipeline: Pipeline | None = session.exec(
        select(Pipeline).where(Pipeline.roi_id == roi.id)
    ).all()[0]

    img = None
    match j:
        case 0:
            img = pipeline.hpf
        case 1:
            img = pipeline.enhanced
        case 2:
            img = pipeline.edges
        case 3:
            img = pipeline.edges_closed

    _, buffer = cv2.imencode(".jpg", img)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.get("/get-number-of-frames")
async def get_number_of_frames(session: SessionDep) -> dict[str, int | float]:
    """
    Restituisce il numero di frame del video prima.
    """
    roi_prima: list[Roi] = roi_controller.get_roi_list(session, Analisi.PRIMA)
    video_path = roi_prima[0].video_path

    video_info = cv2_service.get_video_info(video_path)
    frame_count = video_info["total_frames"]
    return {"total_frames": frame_count}
