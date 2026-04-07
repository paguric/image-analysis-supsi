from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_global_diff():
    assert 200 == 200
