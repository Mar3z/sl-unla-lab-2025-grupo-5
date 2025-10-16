from pydantic import BaseModel, EmailStr #Importa BaseModel para crear modelos Pydantic y EmailStr para validar emails
from datetime import date, time #Importa date para manejar fechas (fecha de nacimiento)
from typing import Optional
from enum import Enum
from schemas import Persona as p

class TurnoBase(BaseModel):
    fecha: date
    hora: time
    persona_id: int

class TurnoCreate(TurnoBase):
    hora: str

class Turno(TurnoBase):
    id: int
    persona: p.Persona
    estado: str = "pendiente"
    
    class Config:
        from_attributes = True

class TurnoUpdate(BaseModel):
    persona_id: Optional[int] = None
    fecha: Optional[date] = None
    hora: Optional[str] = None
    estado: Optional[str] = None
