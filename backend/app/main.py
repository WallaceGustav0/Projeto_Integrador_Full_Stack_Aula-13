"""Rotas da API e entrega do frontend."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import criar_tabela
from .schemas import ReservaEntrada, ReservaSaida, ResumoSaida, Turno
from . import services


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabela()
    yield


app = FastAPI(
    title="API de Reservas de Laboratórios",
    version="1.0.0",
    description="Projeto didático para acompanhar o fluxo completo de uma aplicação Full Stack.",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def abrir_interface():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/reservas", response_model=list[ReservaSaida])
def listar_reservas(
    laboratorio: str | None = Query(default=None, min_length=1),
    turno: Turno | None = None,
):
    return services.listar_reservas(laboratorio, turno.value if turno else None)


@app.get("/api/reservas/resumo", response_model=ResumoSaida)
def obter_resumo():
    return services.obter_resumo()


@app.get("/api/reservas/{reserva_id}", response_model=ReservaSaida)
def consultar_reserva(reserva_id: int):
    reserva = services.buscar_reserva(reserva_id)
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reserva


@app.post("/api/reservas", response_model=ReservaSaida, status_code=status.HTTP_201_CREATED)
def criar_reserva(dados: ReservaEntrada):
    try:
        return services.criar_reserva(dados)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro


@app.put("/api/reservas/{reserva_id}", response_model=ReservaSaida)
def atualizar_reserva(reserva_id: int, dados: ReservaEntrada):
    try:
        reserva = services.atualizar_reserva(reserva_id, dados)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reserva


@app.delete("/api/reservas/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_reserva(reserva_id: int):
    if not services.excluir_reserva(reserva_id):
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
