import pytest
from fastapi.testclient import TestClient
from backend.app import database
from backend.app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Cada teste recebe um banco SQLite novo e isolado."""
    caminho_teste = tmp_path / "reservas_teste.db"
    monkeypatch.setattr(database, "CAMINHO_BANCO", caminho_teste)
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def reserva_valida():
    return {
        "laboratorio": "Laboratório 101",
        "data_reserva": "2026-11-10",
        "turno": "manha",
        "responsavel": "Grupo de Integração",
        "quantidade_pessoas": 20,
        "finalidade": "Aula prática de integração",
    }
