import cv2
import numpy as np
import io

from app.models.roi import Roi
from app.models.roi import Analisi
from app.schemas.roi import RoiData
from app.services import roi_service

from app.dependencies import RoiRepoDep

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/roi")


@router.post("/prima/")
async def get_roi_prima(repo: RoiRepoDep, body: RoiData):
    roi_prima: list[Roi] = roi_service.get_roi_list(repo, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_service.get_roi_list(repo, Analisi.DOPO)

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    patch_prima = roi_prima[body.index].get_pixels(body.frame)
    patch_dopo = roi_dopo[body.index].get_pixels(body.frame)
    # canvas_size = roi_service.get_common_size(patch_prima, patch_dopo)
    canvas_size = roi_service.get_min_size(patch_prima, patch_dopo)
    roi = roi_service.center_patch_on_canvas(patch_prima, canvas_size)

    _, buffer = cv2.imencode(".jpg", roi)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.post("/dopo/")
async def get_roi_dopo(repo: RoiRepoDep, body: RoiData):
    roi_prima: list[Roi] = roi_service.get_roi_list(repo, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_service.get_roi_list(repo, Analisi.DOPO)

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    patch_prima = roi_prima[body.index].get_pixels(body.frame)
    patch_dopo = roi_dopo[body.index].get_pixels(body.frame)
    # canvas_size = roi_service.get_common_size(patch_prima, patch_dopo)
    canvas_size = roi_service.get_min_size(patch_prima, patch_dopo)
    roi = roi_service.center_patch_on_canvas(patch_dopo, canvas_size)

    _, buffer = cv2.imencode(".jpg", roi)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.post("/diff/")
async def get_roi_diff(repo: RoiRepoDep, body: RoiData):
    roi_prima: list[Roi] = roi_service.get_roi_list(repo, Analisi.PRIMA)
    roi_dopo: list[Roi] = roi_service.get_roi_list(repo, Analisi.DOPO)

    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    patch_prima = roi_prima[body.index].get_pixels(body.frame)
    patch_dopo = roi_dopo[body.index].get_pixels(body.frame)
    # canvas_size = roi_service.get_common_size(patch_prima, patch_dopo)
    canvas_size = roi_service.get_min_size(patch_prima, patch_dopo)
    diff = roi_service.center_patch_on_canvas(patch_dopo, canvas_size).astype(
        np.float32
    ) - roi_service.center_patch_on_canvas(patch_prima, canvas_size).astype(np.float32)

    _, buffer = cv2.imencode(".jpg", diff)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.get("/number-of-rois")
async def get_number_of_rois(repo: RoiRepoDep) -> int:
    return len(roi_service.get_roi_list(repo, Analisi.PRIMA))
