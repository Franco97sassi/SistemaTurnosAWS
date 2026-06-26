from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas


# ---------- Clientes ----------

def crear_cliente(db: Session, cliente: schemas.ClienteCreate):
    cliente_existente = db.query(models.Cliente).filter(
        models.Cliente.email == cliente.email
    ).first()

    if cliente_existente:
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese email")

    nuevo_cliente = models.Cliente(**cliente.model_dump())

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente


def obtener_clientes(db: Session):
    return db.query(models.Cliente).all()


# ---------- Profesionales ----------

def crear_profesional(db: Session, profesional: schemas.ProfesionalCreate):
    nuevo_profesional = models.Profesional(**profesional.model_dump())

    db.add(nuevo_profesional)
    db.commit()
    db.refresh(nuevo_profesional)

    return nuevo_profesional


def obtener_profesionales(db: Session):
    return db.query(models.Profesional).all()


# ---------- Estados ----------

def crear_estado(db: Session, estado: schemas.EstadoCreate):
    estado_existente = db.query(models.EstadoTurno).filter(
        models.EstadoTurno.nombre == estado.nombre
    ).first()

    if estado_existente:
        raise HTTPException(status_code=400, detail="Ya existe un estado con ese nombre")

    nuevo_estado = models.EstadoTurno(**estado.model_dump())

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    return nuevo_estado


def obtener_estados(db: Session):
    return db.query(models.EstadoTurno).all()


# ---------- Turnos ----------

def crear_turno(db: Session, turno: schemas.TurnoCreate):
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == turno.cliente_id
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    profesional = db.query(models.Profesional).filter(
        models.Profesional.id == turno.profesional_id
    ).first()

    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    estado = db.query(models.EstadoTurno).filter(
        models.EstadoTurno.id == turno.estado_id
    ).first()

    if not estado:
        raise HTTPException(status_code=404, detail="Estado no encontrado")

    turno_existente = db.query(models.Turno).filter(
        models.Turno.profesional_id == turno.profesional_id,
        models.Turno.fecha_hora == turno.fecha_hora
    ).first()

    if turno_existente:
        raise HTTPException(
            status_code=400,
            detail="El profesional ya tiene un turno en esa fecha y hora"
        )

    nuevo_turno = models.Turno(**turno.model_dump())

    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)

    return nuevo_turno


def obtener_turnos(db: Session):
    return db.query(models.Turno).all()