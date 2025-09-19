from pydantic import BaseModel, EmailStr #Importa BaseModel para crear modelos Pydantic y EmailStr para validar emails
from datetime import date, time #Importa date para manejar fechas (fecha de nacimiento)
from typing import Optional
from enum import Enum

class PersonaBase(BaseModel): #clase base que define los campos obligatorios de una persona
    nombre: str
    email: EmailStr
    dni: str
    telefono: Optional[str] = None
    fecha_nacimiento: date

class PersonaCreate(PersonaBase):#para crear personas (hereda de PersonaBase)
    habilitado: Optional[bool] = True


class Persona(PersonaBase):#para respuestas
    id: int
    edad: int
    habilitado: bool

    class Config:
        orm_mode = True #SQLAlchemy me devuelve los objetos directamente
        from_attributes = True

class PersonaUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    habilitado: Optional[bool] = None

class TurnoBase(BaseModel):
    fecha: date
    hora: time
    persona_id: int

class TurnoCreate(TurnoBase):
    hora: str

class Turno(TurnoBase):
    id: int
    persona: Persona
    estado: str = "pendiente"
    
    class Config:
        from_attributes = True

class TurnoUpdate(BaseModel):
    persona_id: Optional[int] = None
    fecha: Optional[date] = None
    hora: Optional[str] = None
    estado: Optional[str] = None