"""Contratos de entrada e saída da API."""

from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Turno(str, Enum):
    MANHA = "manha"
    TARDE = "tarde"
    NOITE = "noite"


class ReservaEntrada(BaseModel):
    laboratorio: str = Field(min_length=3, max_length=40)
    data_reserva: date
    turno: Turno
    responsavel: str = Field(min_length=3, max_length=80)
    quantidade_pessoas: int = Field(ge=1, le=40)
    finalidade: str = Field(min_length=5, max_length=160)

    @field_validator("laboratorio", "responsavel", "finalidade")
    @classmethod
    def remover_espacos_externos(cls, valor: str) -> str:
        return valor.strip()


class ReservaSaida(ReservaEntrada):
    id: int


class ResumoSaida(BaseModel):
    total: int
    por_turno: dict[str, int]
