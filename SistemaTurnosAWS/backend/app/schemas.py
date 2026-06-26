from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr

# ---------- Cliente ----------

class ClienteBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Profesional ----------

class ProfesionalBase(BaseModel):
    nombre: str
    especialidad: str


class ProfesionalCreate(ProfesionalBase):
    pass


class ProfesionalResponse(ProfesionalBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Estado ----------

class EstadoBase(BaseModel):
    nombre: str


class EstadoCreate(EstadoBase):
    pass


class EstadoResponse(EstadoBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Turno ----------

class TurnoBase(BaseModel):
    cliente_id: int
    profesional_id: int
    estado_id: int
    fecha_hora: datetime
    motivo: str | None = None


class TurnoCreate(TurnoBase):
    pass


class TurnoResponse(TurnoBase):
    id: int

    class Config:
        from_attributes = True