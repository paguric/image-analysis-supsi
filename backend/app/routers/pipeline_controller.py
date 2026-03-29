import io
import os
import cv2

from app.routers import roi_controller
from app.services import pipeline_service
from app.services import roi_service
from app.models.roi import Roi
from app.models.roi import Analisi
from app.schemas.pipeline_params import PipelineParams
from app.db.database import SessionDep

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/pipeline")


@router.post("/")
async def analyze(
    session: SessionDep,
    video_prima: UploadFile = File(...),
    video_dopo: UploadFile = File(...),
) -> dict[str, str]:
    
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

    roi_prima: list[Roi] | None = None
    roi_dopo: list[Roi] | None = None

    roi_prima = pipeline_service.extract_rois(prima_avi_path)
    for roi in roi_prima:
        roi.fase = Analisi.PRIMA
    roi_dopo = pipeline_service.extract_rois(dopo_avi_path)
    for roi in roi_dopo:
        roi.fase = Analisi.DOPO

    # NON DIMENTICARLO
    roi_prima, roi_dopo = roi_service.match_rois_by_center(roi_prima, roi_dopo)

    # Salva ROI nel db
    for roi in roi_prima:
        session.add(roi)
        session.commit()
        session.refresh(roi)

    for roi in roi_dopo:
        session.add(roi)
        session.commit()
        session.refresh(roi)

    return {"TODO": "TODO"}


@router.get("/diff/{frame}/")
def get_diff(session: SessionDep, frame: int) -> StreamingResponse:

    roi_prima: list[Roi] = roi_controller.get_roi_list(session, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_controller.get_roi_list(session, Analisi.DOPO)

    print(len(roi_prima))
    print(len(roi_dopo))

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    diff = roi_service.compute_aligned_roi_diff(roi_prima, roi_dopo, frame)

    _, buffer = cv2.imencode(".jpg", diff)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.post("/roi/{n}")
async def analyze(session: SessionDep, body: PipelineParams) -> StreamingResponse:
    return None