from pydantic import BaseModel, EmailStr #Importa BaseModel para crear modelos Pydantic y EmailStr para validar emails
from datetime import date #Importa date para manejar fechas (fecha de nacimiento)
from typing import Optional

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
