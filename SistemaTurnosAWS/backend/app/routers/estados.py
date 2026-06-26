from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.dependencies import get_db


router = APIRouter(
    prefix="/estados",
    tags=["Estados"]
)


@router.post("/", response_model=schemas.EstadoResponse)
def crear_estado(
    estado: schemas.EstadoCreate,
    db: Session = Depends(get_db)
):
    return crud.crear_estado(db, estado)


@router.get("/", response_model=list[schemas.EstadoResponse])
def obtener_estados(db: Session = Depends(get_db)):
    return crud.obtener_estados(db)