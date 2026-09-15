from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EstadoTurno(str, Enum):
    pendiente = "pendiente"
    cancelado = "cancelado"


class TurnoCreate(BaseModel):
    cliente: str = Field(min_length=2, max_length=100)
    servicio: str = Field(min_length=2, max_length=100)
    fecha: datetime

    @field_validator("cliente", "servicio")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("debe contener al menos 2 caracteres")
        return value

    @field_validator("fecha")
    @classmethod
    def future_date(cls, value: datetime) -> datetime:
        normalized = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if normalized <= datetime.now(timezone.utc):
            raise ValueError("la fecha debe estar en el futuro")
        return normalized


class TurnoUpdate(BaseModel):
    fecha: datetime

    _future_date = field_validator("fecha")(TurnoCreate.future_date.__func__)


class TurnoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente: str
    servicio: str
    fecha: datetime
    estado: EstadoTurno
    created_at: datetime
    updated_at: datetime


class TurnoListResponse(BaseModel):
    items: list[TurnoResponse]
    total: int
    page: int
    page_size: int
