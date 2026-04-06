import io
import os
import sys
import cv2
import numpy as np

from app.services import pipeline_service
from app.services import roi_service
from app.services import cv2_service
from app.services import draw_service
from app.services import video_metadata_service
from app.models.roi import Roi
from app.models.roi import Analisi
from app.models.diff import Diff
from app.models.pipeline import Pipeline
from app.models.video_metadata import VideoMetadata
from app.schemas.pipeline_params import PipelineParams
from app.db.database import SessionDep
from app.dependencies import RoiRepoDep
from app.dependencies import PipelineRepoDep
from app.dependencies import VideoMetadataRepoDep

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from sqlmodel import select


router = APIRouter(prefix="/pipeline")


# NON CANCELLARE
def get_output_dir() -> str:
    # Salva vicino all'exe, non relativo al CWD
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(exe_dir, "out")


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

    output_dir = get_output_dir()
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
        video_path=dopo_avi_path, fase=Analisi.DOPO, brightest_idx=brightest_idx
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
def get_diff(session: SessionDep, repo: RoiRepoDep, frame: int) -> StreamingResponse:
    """
    Calcola il frame differenziale fra le due analisi e lo salva nel db.
    """

    # Se il differenziale è già stato calcolato ed è nel db, lo possiamo restituire subito
    # TODO spostare questa query (come quella in analyze_roi_prima) in un metodo a parte
    result: Diff | None = session.exec(select(Diff).where(Diff.frame == frame)).all()

    if len(result) != 0:
        diff: Diff = result[0]
        # TODO impacchettare queste tre righe per creare l'output in un metodo a parte
        _, buffer = cv2.imencode(".jpg", diff.diff_frame)
        io_buffer = io.BytesIO(buffer)

        return StreamingResponse(io_buffer, media_type="image/jpeg")

    roi_prima: list[Roi] = roi_service.get_roi_list(repo, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_service.get_roi_list(repo, Analisi.DOPO)

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    diff_frame: np.ndarray = roi_service.compute_aligned_roi_diff(
        roi_prima, roi_dopo, frame
    )

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
def get_diff_with_contours(
    session: SessionDep, repo: RoiRepoDep, frame: int
) -> StreamingResponse:
    """
    Applica un overlay verde che permette di identificare le ROI sul differenziale fra le due analisi.
    L'overlay è calcolato come il minEnclosingCircle di raggio minimo fra le due patch.
    """

    roi_prima: list[Roi] = roi_service.get_roi_list(repo, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_service.get_roi_list(repo, Analisi.DOPO)

    # Prende differenziale dal db se già calcolato
    result: Diff | None = session.exec(select(Diff).where(Diff.frame == frame)).all()

    if len(result) != 0:
        diff: Diff = result[0]
        diff_frame: np.ndarray = diff.diff_frame

    # TODO calcola differenziale e salvalo nel db se non esiste

    # Prende come riferimento per il centro le ROI del prima, coerentemente con roi_service.compute_aligned_roi_diff che ricompone il differenziale sui centri delle ROI del prima
    for i, roi in enumerate(roi_prima):
        # Raggio minimo, coerente con calcolo differenziale sempre in roi_service.compute_aligned_roi_diff
        radius = (
            roi_service.get_min_size(
                roi.get_pixels(frame), roi_dopo[i].get_pixels(frame)
            )
            // 2
        )

        # Disegna il minEnclosingCircle sul frame differenziale
        draw_service.draw_circle(
            diff_frame, roi.get_center(), radius=radius, color=(255, 0, 0), filled=False
        )

    _, buffer = cv2.imencode(".jpg", diff_frame)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


def make_roi_analyzer(analisi: Analisi):
    async def endpoint(
        roi_repo: RoiRepoDep,
        pipeline_repo: PipelineRepoDep,
        video_metadata_repo: VideoMetadataRepoDep,
        body: PipelineParams,
        idx: int,
    ):
        """
        Restituisce la nuova ROI identificata dall'applicazione della pipeline sulla singola patch.
        Nota: se nel body della richiesta ci fossero valori mancanti vengono presi quelli di default definiti nello schema della richiesta PipelineParams.
        """
        roi = roi_service.get_roi(roi_repo, idx, analisi)

        # Estrae il frame più luminoso dall'analisi prima
        video_metadata = video_metadata_service.get_video_metadata(
            video_metadata_repo, analisi
        )
        patch = roi.get_pixels(video_metadata.brightest_idx)

        # Applica la pipeline al patch
        pipeline_steps: list[np.ndarray] = pipeline_service.pipeline(patch, body)
        roi_new = pipeline_service.find_valid_contours(pipeline_steps[-1], body)

        """
        OLD (06-04-2026) - Non è responsabilità di questo endpoint!
        In più, non è davvero necessario salvare TUTTO nel db.
        # Salva i singoli step della pipeline nel db
        new_pipeline = Pipeline.from_steps(
            roi_id=roi.id, steps=pipeline_steps, params=body
        )
        pipeline_service.add_pipeline(pipeline_repo, new_pipeline)"""

        # TODO definire Pydantic/SQLModel schema di risposta (aggiungerlo anche alla firma del metodo!)
        # return roi_new
        return None

    return endpoint


router.add_api_route(
    "/roi/prima/{idx}/",
    make_roi_analyzer(Analisi.PRIMA),
    methods=["POST"],
)
router.add_api_route(
    "/roi/dopo/{idx}/",
    make_roi_analyzer(Analisi.DOPO),
    methods=["POST"],
)


def make_pipeline_step_getter(analisi: Analisi):
    async def endpoint(
        roi_repo: RoiRepoDep,
        pipeline_repo: PipelineRepoDep,
        video_metadata_repo: VideoMetadataRepoDep,
        body: PipelineParams,
        idx: int,
        i: int,
    ) -> StreamingResponse:
        """
        Restituisce lo step intermedio i-esimo dell'applicazione della pipeline su una singola ROI dell'analisi prima.
        """
        roi = roi_service.get_roi(roi_repo, idx, analisi)

        # Estrae il frame più luminoso dall'analisi prima
        video_metadata = video_metadata_service.get_video_metadata(
            video_metadata_repo, analisi
        )
        patch = roi.get_pixels(video_metadata.brightest_idx)

        # Applica la pipeline al patch
        img = pipeline_service.pipeline(patch, body)[i]

        """
        OLD (06-04-2026) - Non uso più il db per salvare le applicazioni della pipeline, non ha senso!
        roi = roi_service.get_roi(roi_repo, idx, analisi)
        pipeline: Pipeline = pipeline_service.get_pipeline(pipeline_repo, roi.id)
        img = pipeline.get_step(i)"""

        _, buffer = cv2.imencode(".jpg", img)
        io_buffer = io.BytesIO(buffer)

        return StreamingResponse(io_buffer, media_type="image/jpeg")

    return endpoint


router.add_api_route(
    "/roi/prima/{idx}/step/{i}/",
    make_pipeline_step_getter(Analisi.PRIMA),
    methods=["POST"],
)
router.add_api_route(
    "/roi/dopo/{idx}/step/{i}/",
    make_pipeline_step_getter(Analisi.DOPO),
    methods=["POST"],
)


@router.get("/roi/dopo/{idx}/step/{i}")
async def get_step_pipeline_roi_dopo(
    roi_repo: RoiRepoDep,
    idx: int,
    i: int,
) -> StreamingResponse:
    """
    Restituisce lo step intermedio i-esimo dell'applicazione della pipeline su una singola ROI dell'analisi dopo.
    """
    roi = roi_service.get_roi(roi_repo, idx, Analisi.DOPO)

    pipeline: Pipeline = pipeline_service.get_pipeline(roi_repo, roi.id)

    img = pipeline.get_step(i)

    _, buffer = cv2.imencode(".jpg", img)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.get("/get-number-of-frames")
async def get_number_of_frames(roi_repo: RoiRepoDep) -> dict[str, int | float]:
    """
    Restituisce il numero di frame del video prima.
    """
    roi_prima: list[Roi] = roi_service.get_roi_list(roi_repo, Analisi.PRIMA)
    video_path = roi_prima[0].video_path

    video_info = cv2_service.get_video_info(video_path)
    frame_count = video_info["total_frames"]
    return {"total_frames": frame_count}
