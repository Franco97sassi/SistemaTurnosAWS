from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    telefono = Column(String, nullable=True)

    turnos = relationship("Turno", back_populates="cliente")


class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    especialidad = Column(String, nullable=False)

    turnos = relationship("Turno", back_populates="profesional")


class EstadoTurno(Base):
    __tablename__ = "estados_turno"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)

    turnos = relationship("Turno", back_populates="estado")


class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados_turno.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="turnos")
    profesional = relationship("Profesional", back_populates="turnos")
    estado = relationship("EstadoTurno", back_populates="turnos")