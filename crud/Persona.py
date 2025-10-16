from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from datetime import date, datetime, timedelta, time
from models.Persona import Persona as Persona
from schemas import Persona as SchPersona
from schemas import Turno as SchTurno
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno

# CRUD para Personas
def create_persona(db: Session, persona: SchPersona.PersonaCreate):

    if not persona.dni.isdigit():
        raise HTTPException(status_code=400, detail="El DNI debe ser un valor numérico")

    dniConvertido = int(persona.dni)
    
    #Validaciones de nombre y apellido no vacios y no numericos
    if not persona.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
    if any(char.isdigit() for char in persona.nombre):
        raise HTTPException(status_code=400, detail="El nombre no puede contener números")

    # Validación de DNI
    if dniConvertido < 0:
        raise HTTPException(status_code=400, detail="El DNI no puede ser negativo")
    if len(str(persona.dni)) != 8:
        raise HTTPException(status_code=400, detail="El DNI debe tener 8 dígitos")

    # Validación de fecha de nacimiento
    if persona.fecha_nacimiento > date.today():
        raise HTTPException(status_code=400, detail="La fecha de nacimiento no puede ser futura")

    # Validación de email y dni repetido
    if db.query(Persona).filter(Persona.email == persona.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    if db.query(Persona).filter(Persona.dni == persona.dni).first():
        raise HTTPException(status_code=400, detail="DNI ya registrado")
    
    db_persona = Persona(**persona.dict())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona

def get_personas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Persona).offset(skip).limit(limit).all()

def get_persona(db: Session, persona_id: int):
    return db.query(Persona).filter(Persona.id == persona_id).first()

def update_persona(db: Session, persona_id: int, persona: SchPersona.PersonaUpdate):
    db_persona = get_persona(db, persona_id)
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    update_data = persona.dict(exclude_unset=True)

    if "dni" in update_data:
        if not update_data["dni"].isdigit():
            raise HTTPException(status_code=400, detail="El DNI debe ser un valor numérico")
        dniConvertido = int(persona.dni)
        # Validación de DNI
        if dniConvertido < 0:
            raise HTTPException(status_code=400, detail="El DNI no puede ser negativo")
        if len(str(persona.dni)) != 8:
            raise HTTPException(status_code=400, detail="El DNI debe tener 8 dígitos")

    if "fecha_nacimiento" in update_data:
        # Validación de fecha de nacimiento
        if persona.fecha_nacimiento > date.today():
            raise HTTPException(status_code=400, detail="La fecha de nacimiento no puede ser futura")
    
    for key, value in update_data.items():
        setattr(db_persona, key, value)
    
    db.commit()
    db.refresh(db_persona)
    return db_persona

def delete_persona(db: Session, persona_id: int):
    db_persona = get_persona(db, persona_id)
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    db.delete(db_persona)
    db.commit()
    return {"message": "Persona eliminada correctamente"}