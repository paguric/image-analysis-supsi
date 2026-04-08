from fastapi.testclient import TestClient
import pytest
import os
import cv2
import numpy as np

from app.main import app


def test_csv(client):
    response = client.get("/analysis/diff/results/420/730/")
    assert response.status_code == 200
