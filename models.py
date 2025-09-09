from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base
# Creo la tabla personas
class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    dni = Column(String, unique=True, nullable=False)
    telefono = Column(String)
    fecha_nacimiento = Column(Date)
    edad = Column(Integer)
    habilitado = Column(Boolean, default=True)
