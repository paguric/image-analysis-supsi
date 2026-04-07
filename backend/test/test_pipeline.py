from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)

VIDEO_PRIMA = "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/prima.avi"
VIDEO_DOPO = (
    "/home/lapo225/università/as25-26-sp/prog-semestre/00_image_analysis_unict/dopo.avi"
)


def test_analysis():
    with open(VIDEO_PRIMA, "rb") as f_prima, open(VIDEO_DOPO, "rb") as f_dopo:
        response = client.post(
            "/pipeline/",
            files={
                "video_prima": ("prima.avi", f_prima, "video/x-msvideo"),
                "video_dopo": ("dopo.avi", f_dopo, "video/x-msvideo"),
            },
        )

    assert response.status_code == 200


def test_global_diff():
    response = client.get("/pipeline/diff/100/")
    assert response.status_code == 200
