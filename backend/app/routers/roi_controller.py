import cv2
import numpy as np
import io

from app.models.roi import Roi
from app.schemas.roi import RoiData
from app.services import roi_service

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/roi")


roi_prima: list[Roi] | None = None
roi_dopo: list[Roi] | None = None


@router.post("/prima/")
async def get_roi_prima(body: RoiData):
    patch_prima = roi_prima[body.index].get_pixels(body.frame)
    patch_dopo = roi_dopo[body.index].get_pixels(body.frame)
    canvas_size = roi_service.get_common_size(patch_prima, patch_dopo)
    roi = roi_service.center_patch_on_canvas(patch_prima, canvas_size)

    _, buffer = cv2.imencode(".jpg", roi)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.post("/dopo/")
async def get_roi_dopo(body: RoiData):
    patch_prima = roi_prima[body.index].get_pixels(body.frame)
    patch_dopo = roi_dopo[body.index].get_pixels(body.frame)
    canvas_size = roi_service.get_common_size(patch_prima, patch_dopo)
    roi = roi_service.center_patch_on_canvas(patch_dopo, canvas_size)

    _, buffer = cv2.imencode(".jpg", roi)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


@router.post("/diff/")
async def get_roi_diff(body: RoiData):
    patch_prima = roi_prima[body.index].get_pixels(body.frame)
    patch_dopo = roi_dopo[body.index].get_pixels(body.frame)
    canvas_size = roi_service.get_common_size(patch_prima, patch_dopo)
    diff = roi_service.center_patch_on_canvas(patch_dopo, canvas_size).astype(
        np.float32
    ) - roi_service.center_patch_on_canvas(patch_prima, canvas_size).astype(np.float32)

    _, buffer = cv2.imencode(".jpg", diff)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")
