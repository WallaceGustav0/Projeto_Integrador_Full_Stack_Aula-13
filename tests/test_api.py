def test_fluxo_criar_consultar_atualizar_excluir(client, reserva_valida):
    criada = client.post("/api/reservas", json=reserva_valida)
    assert criada.status_code == 201
    reserva_id = criada.json()["id"]

    consultada = client.get(f"/api/reservas/{reserva_id}")
    assert consultada.status_code == 200
    assert consultada.json()["laboratorio"] == "Laboratório 101"

    alterada = {**reserva_valida, "responsavel": "Grupo B"}
    atualizada = client.put(f"/api/reservas/{reserva_id}", json=alterada)
    assert atualizada.status_code == 200
    assert atualizada.json()["responsavel"] == "Grupo B"

    excluida = client.delete(f"/api/reservas/{reserva_id}")
    assert excluida.status_code == 204
    assert client.get(f"/api/reservas/{reserva_id}").status_code == 404


def test_rejeitar_conflito(client, reserva_valida):
    assert client.post("/api/reservas", json=reserva_valida).status_code == 201
    resposta = client.post("/api/reservas", json=reserva_valida)
    assert resposta.status_code == 409
    assert "Conflito" in resposta.json()["detail"]


def test_rejeitar_quantidade_invalida(client, reserva_valida):
    dados = {**reserva_valida, "quantidade_pessoas": 0}
    resposta = client.post("/api/reservas", json=dados)
    assert resposta.status_code == 422


def test_filtrar_e_resumir(client, reserva_valida):
    client.post("/api/reservas", json=reserva_valida)
    outra = {**reserva_valida, "laboratorio": "Laboratório 202", "turno": "noite"}
    client.post("/api/reservas", json=outra)
    filtradas = client.get("/api/reservas?turno=noite")
    assert filtradas.status_code == 200
    assert len(filtradas.json()) == 1
    resumo = client.get("/api/reservas/resumo")
    assert resumo.json() == {"total": 2, "por_turno": {"manha": 1, "tarde": 0, "noite": 1}}


def test_recurso_inexistente(client):
    assert client.get("/api/reservas/9999").status_code == 404
    assert client.delete("/api/reservas/9999").status_code == 404
