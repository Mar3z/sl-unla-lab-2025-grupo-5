from fastapi import FastAPI, Depends,HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal,engine,Base, get_db  #Me aseguro de que exista database.py con SessionLocal
from models import Persona
from schemas import PersonaCreate,Persona as PersonaSchema
import models
import schemas
import crud
from datetime import date, datetime, time, timedelta
from sqlalchemy.exc import IntegrityError
from typing import List


#Creo tablas
Base.metadata.create_all(bind=engine)
app = FastAPI()

#Endpoint de prueba
"""@app.get("/")
def inicio():
    return {"mensaje": "Probando si funciona la api"}"""


# ----- ENDPOINTS DE PERSONAS (CRUD) -----

# Crear persona / POST
@app.post("/personas", response_model=PersonaSchema)
def crear_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    return crud.create_persona(db, persona)

# Obtener todas las personas / GET
@app.get("/personas", response_model=list[PersonaSchema])
def listar_personas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_personas(db, skip, limit)

# Obtener persona por ID / GET
@app.get("/personas/{persona_id}", response_model=PersonaSchema)
def obtener_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = crud.get_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

# Actualizar personas por id / PUT
@app.put("/personas/{persona_id}", response_model=PersonaSchema)
def actualizar_persona(persona_id: int, persona: schemas.PersonaCreate, db: Session = Depends(get_db)):
    return crud.update_persona(db, persona_id, persona)

# Eliminar personas por id/ DELETE
@app.delete("/personas/{persona_id}")
def eliminar_persona(persona_id: int, db: Session = Depends(get_db)):
    return crud.delete_persona(db, persona_id)

# >>> Endpoints de turnos <<<

@app.post("/turnos", response_model=schemas.Turno, status_code=201)
def crear_turno(turno: schemas.TurnoCreate, db: Session = Depends(get_db)):
    return crud.create_turno(db, turno)

@app.get("/turnos", response_model=list[schemas.Turno])
def listar_turnos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_turnos(db)

@app.get("/turnos/{turno_id}", response_model=schemas.Turno)
def obtener_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = crud.get_turno(db, turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return turno

@app.delete("/turnos/{turno_id}")
def eliminar_turno(turno_id: int, db: Session = Depends(get_db)):
    return crud.delete_turno(db, turno_id)

@app.put("/turnos/{turno_id}", response_model=schemas.Turno)
def actualizar_turno(turno_id: int, turno: schemas.TurnoUpdate, db: Session = Depends(get_db)):
    return crud.update_turno(db, turno_id, turno)


@app.get("/turnos-disponibles")
def turnos_disponibles(fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD"), db: Session = Depends(get_db)):
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Debe ser YYYY-MM-DD")
    
    return crud.get_turnos_disponibles(db, fecha_obj)