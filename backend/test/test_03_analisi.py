import os
import unittest
import pytest
from fastapi.testclient import TestClient
from app.main import app


class AnalysisControllerTest(unittest.TestCase):
    def setUp(self):
        """
        Inizializza il client di test e crea le cartelle dove salvare i file di output per ogni test.
        """
        self.client = TestClient(app)

        os.makedirs("out", exist_ok=True)
        os.makedirs("out/roi", exist_ok=True)
        os.makedirs("out/roi/prima", exist_ok=True)
        os.makedirs("out/roi/dopo", exist_ok=True)

    def tearDown(self):
        return None

    @pytest.mark.skip(reason="")
    def test_csv(self):
        """
        Verifica /analysis/diff/results/{min_freq}/{max_freq}/ (calcolo CSV globale).
        """
        response = self.client.get("/analysis/diff/results/420/730/")
        assert response.status_code == 200
