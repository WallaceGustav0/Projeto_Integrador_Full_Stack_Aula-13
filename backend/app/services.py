"""CRUD e regras de negócio, separados das rotas HTTP."""

import sqlite3
from .database import conectar
from .schemas import ReservaEntrada


def _linha_para_dict(linha: sqlite3.Row) -> dict:
    return dict(linha)


def listar_reservas(laboratorio: str | None = None, turno: str | None = None) -> list[dict]:
    consulta = "SELECT * FROM reservas WHERE 1=1"
    parametros: list[str] = []
    if laboratorio:
        consulta += " AND laboratorio LIKE ?"
        parametros.append(f"%{laboratorio.strip()}%")
    if turno:
        consulta += " AND turno = ?"
        parametros.append(turno)
    consulta += " ORDER BY data_reserva, turno, laboratorio"
    with conectar() as conexao:
        linhas = conexao.execute(consulta, parametros).fetchall()
    return [_linha_para_dict(linha) for linha in linhas]


def buscar_reserva(reserva_id: int) -> dict | None:
    with conectar() as conexao:
        linha = conexao.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,)).fetchone()
    return _linha_para_dict(linha) if linha else None


def existe_conflito(dados: ReservaEntrada, ignorar_id: int | None = None) -> bool:
    consulta = """
        SELECT 1 FROM reservas
        WHERE laboratorio = ? AND data_reserva = ? AND turno = ?
    """
    parametros: list[object] = [dados.laboratorio, dados.data_reserva.isoformat(), dados.turno.value]
    if ignorar_id is not None:
        consulta += " AND id != ?"
        parametros.append(ignorar_id)
    with conectar() as conexao:
        return conexao.execute(consulta, parametros).fetchone() is not None


def criar_reserva(dados: ReservaEntrada) -> dict:
    if existe_conflito(dados):
        raise ValueError("Conflito: laboratório já reservado nessa data e turno")
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO reservas
            (laboratorio, data_reserva, turno, responsavel, quantidade_pessoas, finalidade)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                dados.laboratorio,
                dados.data_reserva.isoformat(),
                dados.turno.value,
                dados.responsavel,
                dados.quantidade_pessoas,
                dados.finalidade,
            ),
        )
        reserva_id = cursor.lastrowid
    return buscar_reserva(reserva_id)


def atualizar_reserva(reserva_id: int, dados: ReservaEntrada) -> dict | None:
    if buscar_reserva(reserva_id) is None:
        return None
    if existe_conflito(dados, ignorar_id=reserva_id):
        raise ValueError("Conflito: laboratório já reservado nessa data e turno")
    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE reservas SET laboratorio=?, data_reserva=?, turno=?, responsavel=?,
            quantidade_pessoas=?, finalidade=? WHERE id=?
            """,
            (
                dados.laboratorio,
                dados.data_reserva.isoformat(),
                dados.turno.value,
                dados.responsavel,
                dados.quantidade_pessoas,
                dados.finalidade,
                reserva_id,
            ),
        )
    return buscar_reserva(reserva_id)


def excluir_reserva(reserva_id: int) -> bool:
    with conectar() as conexao:
        cursor = conexao.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    return cursor.rowcount > 0


def obter_resumo() -> dict:
    reservas = listar_reservas()
    por_turno = {"manha": 0, "tarde": 0, "noite": 0}
    for reserva in reservas:
        por_turno[reserva["turno"]] += 1
    return {"total": len(reservas), "por_turno": por_turno}
