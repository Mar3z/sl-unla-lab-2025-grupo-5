from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time

class TurnoInfo(BaseModel):
    id: int
    fecha: date
    hora: time
    nombre_persona: str
    dni_persona: str
    estado: str

    class Config:
        from_attributes = True

class TurnoInfoBasica(BaseModel):
    id: int
    fecha: date
    hora: time
    estado: str

class TurnoCanceladoInfo(BaseModel):
    id: int
    persona_id: int
    fecha: date
    hora: time
    estado: str

    class Config:
        from_attributes = True

class CanceladosMesEnCurso(BaseModel):
    anio: int
    mes: str
    cantidad: int
    turnos: List[TurnoCanceladoInfo]

class TurnoCanceladoInfoBasico(BaseModel):
    id: int
    fecha: date
    hora: time

class PersonasConTurnosCancelados(BaseModel):
    id_usuario: int
    nombre: str
    cantidad_cancelados: int
    turnos_cancelados: List[TurnoCanceladoInfoBasico]

class TurnosPorPersona(BaseModel):
    id_persona: int
    nombre: str
    turnos: List[TurnoInfoBasica]
