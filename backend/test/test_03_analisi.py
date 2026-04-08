from fastapi.testclient import TestClient
import pytest
import os
import cv2
import numpy as np

from app.main import app


def test_csv(client):
    """
    Testa che questa funzione cv2.drawContours(mask, [contours], 0, 255, -1) faccia effettivamente il suo lavoro
    """

    response = client.get("/analysis/diff/results/")

    assert response.status_code == 200
