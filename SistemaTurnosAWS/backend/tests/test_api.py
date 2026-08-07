import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.database import SessionLocal
from app.main import cancelar_turno, crear_turno, health, listar_turnos
from app.schemas import TurnoCreate


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_health_check():
    assert health() == {"status": "ok"}


def test_turno_lifecycle(db):
    created = crear_turno(
        TurnoCreate.model_validate({
            "cliente": "  Ada Lovelace  ",
            "servicio": "Consultoría",
            "fecha": "2030-05-10T14:30:00",
        }),
        db,
    )
    assert created.cliente == "Ada Lovelace"
    assert created.estado == "pendiente"

    assert len(listar_turnos(db)) == 1

    assert cancelar_turno(created.id, db) == {"mensaje": "Turno cancelado correctamente"}
    assert listar_turnos(db)[0].estado == "cancelado"


def test_invalid_turno_is_rejected():
    with pytest.raises(ValidationError):
        TurnoCreate.model_validate(
            {"cliente": " ", "servicio": "A", "fecha": "not-a-date"}
        )


def test_missing_turno_returns_404(db):
    with pytest.raises(HTTPException) as error:
        cancelar_turno(9999, db)
    assert error.value.status_code == 404
