import cv2
import numpy as np
import io

from app.models.roi import Roi
from app.models.enums import Analisi
from app.schemas.roi import RoiData
from app.schemas.roi import RoiResponse
from app.services import roi_service

from app.dependencies import RoiRepoDep

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/roi")


def make_roi_patch_getter(analisi: Analisi):
    async def endpoint(
        roi_repo: RoiRepoDep,
        body: RoiData,
    ) -> StreamingResponse:
        roi_prima: list[Roi] = roi_service.get_roi_list(roi_repo, Analisi.PRIMA)
        roi_dopo: list[Roi] = roi_service.get_roi_list(roi_repo, Analisi.DOPO)

        if roi_prima is None or roi_dopo is None:
            raise HTTPException(status_code=400, detail="No images uploaded yet")

        patch_prima = roi_service.get_roi(
            roi_repo, body.index, Analisi.PRIMA
        ).get_pixels(body.frame)
        patch_dopo = roi_service.get_roi(roi_repo, body.index, Analisi.DOPO).get_pixels(
            body.frame
        )

        # OLD
        """patch_prima = roi_prima[body.index].get_pixels(body.frame)
        patch_dopo = roi_dopo[body.index].get_pixels(body.frame)"""

        canvas_size = roi_service.get_min_size(patch_prima, patch_dopo)

        match analisi:
            case Analisi.PRIMA:
                patch = roi_service.center_patch_on_canvas(
                    patch_prima, canvas_size
                ).astype(np.float32)
            case Analisi.DOPO:
                patch = roi_service.center_patch_on_canvas(
                    patch_dopo, canvas_size
                ).astype(np.float32)
            case Analisi.DIFF:
                patch_prima = roi_service.center_patch_on_canvas(
                    patch_prima, canvas_size
                ).astype(np.float32)
                patch_dopo = roi_service.center_patch_on_canvas(
                    patch_dopo, canvas_size
                ).astype(np.float32)
                patch = patch_dopo - patch_prima

        _, buffer = cv2.imencode(".jpg", patch)
        io_buffer = io.BytesIO(buffer)

        return StreamingResponse(io_buffer, media_type="image/jpeg")

    return endpoint


router.add_api_route(
    "/prima/",
    make_roi_patch_getter(Analisi.PRIMA),
    methods=["POST"],
)
router.add_api_route(
    "/dopo/",
    make_roi_patch_getter(Analisi.DOPO),
    methods=["POST"],
)
router.add_api_route(
    "/diff/",
    make_roi_patch_getter(Analisi.DIFF),
    methods=["POST"],
)


@router.post("/save/")
def save_new_roi(roi_repo: RoiRepoDep, body: RoiResponse):
    """
    Sostituisce la ROI ricevuta nel body alla ROI corrispondente nel db.
    Restituisce la vecchia ROI.
    """

    roi_old = roi_repo.get(body.idx, body.fase)

    if not roi_repo.delete(roi_old.id):
        raise HTTPException(status_code=404, detail="ROI not found")

    roi_repo.add(roi_service.response_to_roi(body))

    return roi_service.roi_to_response(roi_old)


@router.get("/number-of-rois")
async def get_number_of_rois(repo: RoiRepoDep) -> int:
    return len(roi_service.get_roi_list(repo, Analisi.PRIMA))
