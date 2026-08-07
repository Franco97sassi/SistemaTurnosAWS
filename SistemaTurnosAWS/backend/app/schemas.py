from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime


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


class TurnoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente: str
    servicio: str
    fecha: datetime
    estado: str
