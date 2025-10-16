from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time

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