from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.dependencies import get_db


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.post("/", response_model=schemas.ClienteResponse)
def crear_cliente(
    cliente: schemas.ClienteCreate,
    db: Session = Depends(get_db)
):
    return crud.crear_cliente(db, cliente)


@router.get("/", response_model=list[schemas.ClienteResponse])
def obtener_clientes(
    db: Session = Depends(get_db)
):
    return crud.obtener_clientes(db)