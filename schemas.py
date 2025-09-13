from pydantic import BaseModel, EmailStr #Importa BaseModel para crear modelos Pydantic y EmailStr para validar emails
from datetime import date #Importa date para manejar fechas (fecha de nacimiento)
from typing import Optional

class PersonaBase(BaseModel): #clase base que define los campos obligatorios de una persona
    nombre: str
    email: EmailStr
    dni: str
    telefono: str
    fecha_nacimiento: date

class PersonaCreate(PersonaBase):#para crear personas (hereda de PersonaBase)
    pass

class Persona(PersonaBase):#para respuestas
    id: int
    edad: int
    habilitado: bool

    class Config:
        orm_mode = True #SQLAlchemy me devuelve los objetos directamente


# Schemas para Turno
class TurnoBase(BaseModel):
    fecha: date
    hora: str  # "HH:MM"
    estado: Optional[str] = None  # opcional en entrada (en creación forzaremos 'pendiente')

class TurnoCreate(TurnoBase):
    persona_id: int

class TurnoUpdate(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[str] = None
    estado: Optional[str] = None

class Turno(TurnoBase):
    id: int
    persona: Persona

    class Config:
        orm_mode = True
