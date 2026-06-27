from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    servicio = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False)
    estado = Column(String, default="pendiente")