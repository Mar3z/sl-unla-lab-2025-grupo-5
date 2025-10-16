#Importamos los tipos de datos que vamos a usar en la tabla
#Column para definir columnas.Integer, String, Date, Boolean (tipos de datos de las columnas)
from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Enum, ForeignKey

#Importamos la clase Base que creamos en database.py (con declarative_base())
#Esta clase es la base de todos nuestros modelos/tablas
from database import Base

from datetime import date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Turno(Base):
    __tablename__ = "turnos"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String, default="pendiente")
    persona_id = Column(Integer, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    
    persona = relationship("Persona", back_populates="turnos")