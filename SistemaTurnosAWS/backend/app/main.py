from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from .database import Base, engine, SessionLocal
from .models import Turno
from .schemas import TurnoCreate, TurnoResponse
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

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


@app.get("/turnos", response_model=List[TurnoResponse])
def listar_turnos(db: Session = Depends(get_db)):
    return db.query(Turno).all()


@app.delete("/turnos/{turno_id}")
def cancelar_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()

    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    turno.estado = "cancelado"
    db.commit()

    return {"mensaje": "Turno cancelado correctamente"}
