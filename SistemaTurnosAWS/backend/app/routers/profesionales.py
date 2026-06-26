from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.dependencies import get_db


router = APIRouter(
    prefix="/profesionales",
    tags=["Profesionales"]
)


@router.post("/", response_model=schemas.ProfesionalResponse)
def crear_profesional(
    profesional: schemas.ProfesionalCreate,
    db: Session = Depends(get_db)
):
    return crud.crear_profesional(db, profesional)


@router.get("/", response_model=list[schemas.ProfesionalResponse])
def obtener_profesionales(db: Session = Depends(get_db)):
    return crud.obtener_profesionales(db)