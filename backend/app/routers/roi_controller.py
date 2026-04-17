import cv2
import numpy as np
import io

from app.models.roi import Roi
from app.models.enums import Analisi
from app.schemas.roi import RoiData
from app.schemas.roi import RoiResponse
from app.services import roi_service
from app.services import draw_service

from app.dependencies import RoiRepoDep

from fastapi import APIRouter
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/roi")


def make_roi_patch_getter(analisi: Analisi):
    async def endpoint(
        roi_repo: RoiRepoDep,
        body: RoiData,
    ) -> StreamingResponse:

        roi_prima = roi_service.get_roi(roi_repo, body.index, Analisi.PRIMA)
        roi_dopo = roi_service.get_roi(roi_repo, body.index, Analisi.DOPO)

        patch_prima = roi_prima.get_pixels(body.frame)
        patch_dopo = roi_dopo.get_pixels(body.frame)

        canvas_size = roi_service.get_min_size(patch_prima, patch_dopo)

        # Porta le patch alla stessa dimensione
        patch_prima = roi_service.center_patch_on_canvas(
            patch_prima, canvas_size
        ).astype(np.float32)
        patch_dopo = roi_service.center_patch_on_canvas(patch_dopo, canvas_size).astype(
            np.float32
        )

        match analisi:
            case Analisi.PRIMA:
                patch = patch_prima
                draw_service.draw_contour(
                    patch, roi_prima.get_local_contours(), (255, 0, 0)
                )
            case Analisi.DOPO:
                patch = patch_dopo
                draw_service.draw_contour(
                    patch, roi_dopo.get_local_contours(), (255, 0, 0)
                )
            case Analisi.DIFF:
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
    Sostituisce i contorni della ROI nel db con quelli della ROI passata nel body.
    """

    roi_old = roi_repo.get(body.idx, body.fase)
    roi_new = roi_service.response_to_roi(body)
    roi_old.contours = roi_new.contours


@router.get("/number-of-rois")
async def get_number_of_rois(repo: RoiRepoDep) -> int:
    return len(roi_service.get_roi_list(repo, Analisi.PRIMA))
