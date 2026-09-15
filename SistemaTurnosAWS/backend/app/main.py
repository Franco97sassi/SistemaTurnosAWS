import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Turno
from .schemas import TurnoCreate, TurnoListResponse, TurnoResponse, TurnoUpdate

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger("turnos")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app = FastAPI(
    title="Sistema de Turnos AWS",
    version=os.getenv("APP_VERSION", "1.0.0"),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed request_id=%s path=%s", request_id, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno", "request_id": request_id},
        )
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"mensaje": "API Sistema de Turnos funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/turnos", response_model=TurnoResponse)
def crear_turno(turno: TurnoCreate, db: Session = Depends(get_db)):
    conflict = db.scalar(
        select(Turno).where(
            Turno.fecha == turno.fecha,
            Turno.estado == "pendiente",
        )
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Ya existe un turno para esa fecha")

    nuevo_turno = Turno(
        cliente=turno.cliente,
        servicio=turno.servicio,
        fecha=turno.fecha,
        estado="pendiente"
    )

    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)

    return nuevo_turno


@app.get("/turnos", response_model=TurnoListResponse)
def listar_turnos(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 12,
    estado: Literal["pendiente", "cancelado"] | None = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
    db: Session = Depends(get_db),
):
    filters = []
    if estado:
        filters.append(Turno.estado == estado)
    if search:
        term = f"%{search.strip()}%"
        filters.append(Turno.cliente.ilike(term) | Turno.servicio.ilike(term))

    total = db.scalar(select(func.count(Turno.id)).where(*filters)) or 0
    items = db.scalars(
        select(Turno)
        .where(*filters)
        .order_by(Turno.fecha.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@app.patch("/turnos/{turno_id}", response_model=TurnoResponse)
def reprogramar_turno(turno_id: int, update: TurnoUpdate, db: Session = Depends(get_db)):
    turno = db.get(Turno, turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    if turno.estado == "cancelado":
        raise HTTPException(status_code=409, detail="No se puede reprogramar un turno cancelado")
    conflict = db.scalar(
        select(Turno).where(
            Turno.fecha == update.fecha,
            Turno.estado == "pendiente",
            Turno.id != turno_id,
        )
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Ya existe un turno para esa fecha")
    turno.fecha = update.fecha
    db.commit()
    db.refresh(turno)
    return turno


@app.delete("/turnos/{turno_id}")
def cancelar_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.get(Turno, turno_id)

    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    turno.estado = "cancelado"
    db.commit()

    return {"mensaje": "Turno cancelado correctamente"}
