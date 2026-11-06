from datetime import date
import pytest
from backend.app.schemas import ReservaEntrada
from backend.app import services


def criar_modelo():
    return ReservaEntrada(
        laboratorio="Laboratório 303",
        data_reserva=date(2026, 11, 11),
        turno="tarde",
        responsavel="Equipe de Serviços",
        quantidade_pessoas=12,
        finalidade="Teste direto da regra de negócio",
    )


def test_servico_cria_e_localiza(client):
    criada = services.criar_reserva(criar_modelo())
    assert criada["id"] > 0
    assert services.buscar_reserva(criada["id"])["turno"] == "tarde"


def test_servico_impede_conflito(client):
    services.criar_reserva(criar_modelo())
    with pytest.raises(ValueError, match="Conflito"):
        services.criar_reserva(criar_modelo())
