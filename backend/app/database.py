"""Acesso ao SQLite. Mantido simples para facilitar a leitura em aula."""

from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
CAMINHO_BANCO = BASE_DIR / "dados" / "reservas.db"


def conectar() -> sqlite3.Connection:
    """Abre uma conexão e permite acessar colunas pelo nome."""
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela() -> None:
    """Prepara a tabela antes de a API receber requisições."""
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                laboratorio TEXT NOT NULL,
                data_reserva TEXT NOT NULL,
                turno TEXT NOT NULL,
                responsavel TEXT NOT NULL,
                quantidade_pessoas INTEGER NOT NULL,
                finalidade TEXT NOT NULL,
                UNIQUE(laboratorio, data_reserva, turno)
            )
            """
        )
