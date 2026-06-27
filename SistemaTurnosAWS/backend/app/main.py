from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, SessionLocal
from .models import Turno
from .schemas import TurnoCreate, TurnoResponse
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Turnos AWS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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