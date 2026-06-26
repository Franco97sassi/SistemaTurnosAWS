from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.dependencies import get_db


router = APIRouter(
    prefix="/turnos",
    tags=["Turnos"]
)


@router.post("/", response_model=schemas.TurnoResponse)
def crear_turno(
    turno: schemas.TurnoCreate,
    db: Session = Depends(get_db)
):
    return crud.crear_turno(db, turno)


@router.get("/", response_model=list[schemas.TurnoResponse])
def obtener_turnos(db: Session = Depends(get_db)):
    return crud.obtener_turnos(db)