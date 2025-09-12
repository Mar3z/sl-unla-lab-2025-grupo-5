from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base
from datetime import date

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

    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) <
            (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
