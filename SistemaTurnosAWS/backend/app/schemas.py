from pydantic import BaseModel
from datetime import datetime

class TurnoCreate(BaseModel):
    cliente: str
    servicio: str
    fecha: datetime

class TurnoResponse(BaseModel):
    id: int
    cliente: str
    servicio: str
    fecha: datetime
    estado: str

    class Config:
        from_attributes = True