from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from .database import Base

class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(100), nullable=False, index=True)
    servicio = Column(String(100), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), nullable=False, index=True)
    estado = Column(String(20), nullable=False, default="pendiente", index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
