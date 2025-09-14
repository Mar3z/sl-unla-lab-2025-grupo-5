from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Enum, ForeignKey
from database import Base
from datetime import date
from sqlalchemy.orm import relationship

# Creo la tabla personas
class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    dni = Column(String, unique=True, nullable=False)
    telefono = Column(String)
    fecha_nacimiento = Column(Date)
    habilitado = Column(Boolean, default=True)

    turnos = relationship("Turno", back_populates="persona")

    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) <
            (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )


class Turno(Base):
    __tablename__ = "turnos"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String, default="pendiente")
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    
    persona = relationship("Persona", back_populates="turnos")