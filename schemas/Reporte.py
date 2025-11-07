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

class TurnoCanceladoInfoBasico(BaseModel):
    id: int
    fecha: date
    hora: time

class TurnoCanceladoInfo(BaseModel):
    persona_id: int
    nombre: str
    turnos: List[TurnoCanceladoInfoBasico]

class TurnosSinFecha(BaseModel):
    id: int
    hora: time
    persona_nombre: str
    estado: str

class TurnosPorFecha(BaseModel):
    fecha: date
    turnos: List[TurnosSinFecha]

class CanceladosMesEnCurso(BaseModel):
    anio: int
    mes: str
    cantidad: int
    turnos: List[TurnoCanceladoInfo]

class PersonasConTurnosCancelados(BaseModel):
    id_usuario: int
    nombre: str
    cantidad_cancelados: int
    turnos_cancelados: List[TurnoCanceladoInfoBasico]

class TurnosPorPersona(BaseModel):
    id_persona: int
    nombre: str
    turnos: List[TurnoInfoBasica]
