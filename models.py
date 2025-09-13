
#Importamos los tipos de datos que vamos a usar en la tabla
#Column para definir columnas.Integer, String, Date, Boolean (tipos de datos de las columnas)
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

#Importamos la clase Base que creamos en database.py (con declarative_base())
#Esta clase es la base de todos nuestros modelos/tablas
from database import Base


from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base

# Creo la tabla personas
class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    dni = Column(Integer, unique=True, nullable=False)
    telefono = Column(Integer)
    fecha_nacimiento = Column(Date)
    edad = Column(Integer)
    habilitado = Column(Boolean, default=True)

    # Establece relacion con Turno
    turnos = relationship("Turno", back_populates="persona", cascade="all, delete-orphan")

    class Turno(Base):
       __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)         # fecha del turno
    hora = Column(String, nullable=False)        # formato "HH:MM"
    estado = Column(String, default="pendiente") # pendiente, cancelado, confirmado, asistido. Por defecto al crear PENDIENTE
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)

    persona = relationship("Persona", back_populates="turnos")

    
