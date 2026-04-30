import io
import os
import sys
import cv2
import numpy as np

from app.services import pipeline_service
from app.services import roi_service
from app.services import draw_service
from app.services import video_metadata_service
from app.models.roi import Roi
from app.models.enums import Analisi
from app.models.diff import Diff
from app.models.pipeline import Pipeline
from app.models.video_metadata import VideoMetadata
from app.schemas.pipeline_params import PipelineParams
from app.schemas.roi import RoiResponse
from app.schemas.analyze_request import AnalyzeRequest
from app.db.database import SessionDep
from app.dependencies import RoiRepoDep
from app.dependencies import PipelineRepoDep
from app.dependencies import VideoMetadataRepoDep

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from sqlmodel import select

from app.bootstrapper import get_out_dir

router = APIRouter(prefix="/pipeline")


# NON CANCELLARE
def get_output_dir() -> str:
    # Salva vicino all'exe, non relativo al CWD
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(exe_dir, "out")


@router.post("/", deprecated=True)
async def analyze(
    session: SessionDep,
    roi_repo: RoiRepoDep,
    video_metadata_repo: VideoMetadataRepoDep,
    video_prima: UploadFile = File(...),
    video_dopo: UploadFile = File(...),
):
    """
    Estrae le ROI dai video delle due analisi e le salva nel db.
    Questo endpoint è stato sostituito da /pipeline/local/ che andrebbe usato al posto di questo.
    """

    prima_bytes = await video_prima.read()
    dopo_bytes = await video_dopo.read()

    output_dir = get_out_dir()
    output_dir.mkdir(exist_ok=True)
    prima_avi_path = str(output_dir / "prima.avi")
    dopo_avi_path = str(output_dir / "dopo.avi")

    # Salva i file caricati
    with open(prima_avi_path, "wb") as f:
        f.write(prima_bytes)
    with open(dopo_avi_path, "wb") as f:
        f.write(dopo_bytes)

    # Estrae tramite video_metadata_service tutti i metadati dei video e li salva nel db
    video_metadata_service.add_video_metadata_from_path(
        video_metadata_repo, prima_avi_path, Analisi.PRIMA
    )
    video_metadata_service.add_video_metadata_from_path(
        video_metadata_repo, dopo_avi_path, Analisi.DOPO
    )

    # Estrai le ROI e aggiungi i metadati necessari
    roi_prima: list[Roi] = pipeline_service.extract_rois(
        video_metadata_service.get_video_metadata(
            video_metadata_repo, Analisi.PRIMA
        ).brightest_frame
    )
    for roi in roi_prima:
        roi.video_path = prima_avi_path
        roi.fase = Analisi.PRIMA

    roi_dopo: list[Roi] = pipeline_service.extract_rois(
        video_metadata_service.get_video_metadata(
            video_metadata_repo, Analisi.DOPO
        ).brightest_frame
    )
    for roi in roi_dopo:
        roi.video_path = dopo_avi_path
        roi.fase = Analisi.DOPO

    # Dopo aver calcolato le ROI, assegna lo stesso indice
    roi_prima, roi_dopo = roi_service.match_rois_by_center(roi_prima, roi_dopo)

    # Salva ROI nel db
    for roi in roi_prima + roi_dopo:
        roi_service.add_roi(roi_repo, roi)


@router.post("/local/")
async def analyze_local(
    roi_repo: RoiRepoDep,
    video_metadata_repo: VideoMetadataRepoDep,
    body: AnalyzeRequest,
):
    # Estrae tramite video_metadata_service tutti i metadati dei video e li salva nel db
    video_metadata_service.add_video_metadata_from_path(
        video_metadata_repo, body.video_prima, Analisi.PRIMA
    )
    video_metadata_service.add_video_metadata_from_path(
        video_metadata_repo, body.video_dopo, Analisi.DOPO
    )

    # Estrai le ROI e aggiungi i metadati necessari
    roi_prima: list[Roi] = pipeline_service.extract_rois(
        video_metadata_service.get_video_metadata(
            video_metadata_repo, Analisi.PRIMA
        ).brightest_frame
    )
    for roi in roi_prima:
        roi.video_path = body.video_prima
        roi.fase = Analisi.PRIMA

    roi_dopo: list[Roi] = pipeline_service.extract_rois(
        video_metadata_service.get_video_metadata(
            video_metadata_repo, Analisi.DOPO
        ).brightest_frame
    )
    for roi in roi_dopo:
        roi.video_path = body.video_dopo
        roi.fase = Analisi.DOPO

    # Dopo aver calcolato le ROI, assegna lo stesso indice
    roi_prima, roi_dopo = roi_service.match_rois_by_center(roi_prima, roi_dopo)

    # Salva ROI nel db
    for roi in roi_prima + roi_dopo:
        roi_service.add_roi(roi_repo, roi)


@router.get("/diff/{frame}/")
def get_diff(
    session: SessionDep, roi_repo: RoiRepoDep, frame: int
) -> StreamingResponse:
    """
    Calcola il frame differenziale fra le due analisi.
    """
    diff_frame = roi_service.compute_aligned_roi_diff(roi_repo, frame)

    _, buffer = cv2.imencode(".jpg", diff_frame)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.get("/diff/{frame}/contours/")
def get_diff_with_contours(
    session: SessionDep, roi_repo: RoiRepoDep, frame: int
) -> StreamingResponse:
    """
    Calcola il frame differenziale, poi applica un overlay verde che permette di identificare le ROI sul differenziale fra le due analisi.
    L'overlay è calcolato come il minEnclosingCircle di raggio minimo fra le due patch.
    Viene aggiunto anche un indice per identificare le ROI.
    """
    diff_frame = roi_service.compute_aligned_roi_diff(roi_repo, frame)
    # Riconverte diff_frame in immagine a colori con 3 canali per pixel, in modo da disegnare correttamente i bordi colorati
    diff_frame = cv2.cvtColor(diff_frame, cv2.COLOR_GRAY2BGR)
    roi_prima = roi_service.get_roi_list(roi_repo, Analisi.PRIMA)
    roi_dopo = roi_service.get_roi_list(roi_repo, Analisi.DOPO)

    # Prende come riferimento per il centro le ROI del prima, coerentemente con roi_service.compute_aligned_roi_diff che ricompone il differenziale sui centri delle ROI del prima
    for i, roi_l in enumerate(roi_prima):
        # Raggio minimo, coerente con calcolo differenziale sempre in roi_service.compute_aligned_roi_diff
        radius = (
            roi_service.get_min_size(
                roi_l.get_pixels(frame), roi_dopo[i].get_pixels(frame)
            )
            // 2
        )

        # Disegna il minEnclosingCircle sul frame differenziale
        draw_service.draw_circle(
            diff_frame,
            roi_l.get_center(),
            radius=radius,
            color=(255, 0, 0),
            filled=False,
        )

        # Applica indice sull'angolo in alto a sx
        x, y, w, h = cv2.boundingRect(roi_l.contours)
        draw_service.draw_label(diff_frame, (roi_l.idx + 1), (x, y), (0, 255, 0), 0.8)

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
    ) -> RoiResponse:
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
        roi_new = pipeline_service.extract_rois(patch, body)[0]

        # Clona i valori (tranne i contorni) della ROI originale
        roi_new.idx = roi.idx
        roi_new.video_path = roi.video_path
        roi_new.fase = roi.fase

        """
        OLD (06-04-2026) - Non è responsabilità di questo endpoint!
        In più, non è davvero necessario salvare TUTTO nel db.
        # Salva i singoli step della pipeline nel db
        new_pipeline = Pipeline.from_steps(
            roi_id=roi.id, steps=pipeline_steps, params=body
        )
        pipeline_service.add_pipeline(pipeline_repo, new_pipeline)"""

        # Pydantic BaseModel della Roi
        return roi_service.roi_to_response(roi_new)

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
        Restituisce lo step intermedio i-esimo (zero based) dell'applicazione della pipeline su una singola ROI dell'analisi prima.
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


@router.get("/get-number-of-frames")
async def get_number_of_frames(roi_repo: RoiRepoDep) -> dict[str, int | float]:
    """
    Restituisce il numero di frame del video prima e dopo.
    """
    roi_prima: list[Roi] = roi_service.get_roi_list(roi_repo, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_service.get_roi_list(roi_repo, Analisi.DOPO)

    video_path_prima = roi_prima[0].video_path
    video_path_dopo = roi_dopo[0].video_path

    video_prima_info = video_metadata_service.get_video_info(video_path_prima)
    video_dopo_info = video_metadata_service.get_video_info(video_path_dopo)

    frame_count_prima = video_prima_info["total_frames"]
    frame_count_dopo = video_dopo_info["total_frames"]

    return {
        "total_frames_prima": frame_count_prima,
        "total_frames_dopo": frame_count_dopo,
    }
