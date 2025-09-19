from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
import models
import schemas
from fastapi import HTTPException

# CRUD para Personas
def create_persona(db: Session, persona: schemas.PersonaCreate):

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
    if db.query(models.Persona).filter(models.Persona.email == persona.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    if db.query(models.Persona).filter(models.Persona.dni == persona.dni).first():
        raise HTTPException(status_code=400, detail="DNI ya registrado")
    
    db_persona = models.Persona(**persona.dict())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona

def get_personas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Persona).offset(skip).limit(limit).all()

def get_persona(db: Session, persona_id: int):
    return db.query(models.Persona).filter(models.Persona.id == persona_id).first()

def update_persona(db: Session, persona_id: int, persona: schemas.PersonaUpdate):
    db_persona = get_persona(db, persona_id)
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    update_data = persona.dict(exclude_unset=True)
    dniConvertido = int(persona.dni)
    # Validación de DNI
    if dniConvertido < 0:
        raise HTTPException(status_code=400, detail="El DNI no puede ser negativo")
    if len(str(persona.dni)) != 8:
        raise HTTPException(status_code=400, detail="El DNI debe tener 8 dígitos")

    # Validación de fecha de nacimiento
    if persona.fecha_nacimiento > date.today():
        raise HTTPException(status_code=400, detail="La fecha de nacimiento no puede ser futura")
    
    for key, value in persona.dict().items():
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

# CRUD para Turnos
def get_turnos_cancelados_recientes(db: Session, persona_id: int):
    seis_meses_atras = date.today() - timedelta(days=180)
    
    return db.query(models.Turno).filter(
        and_(
            models.Turno.persona_id == persona_id,
            models.Turno.estado == "cancelado",
            models.Turno.fecha >= seis_meses_atras
        )
    ).count()

def create_turno(db: Session, turno: schemas.TurnoCreate):
    # Verificar si la persona existe
    persona = db.query(models.Persona).filter(models.Persona.id == turno.persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    # Verificar regla de negocio: máximo 5 turnos cancelados en últimos 6 meses
    turnos_cancelados = get_turnos_cancelados_recientes(db, turno.persona_id)
    if turnos_cancelados >= 5:
        raise HTTPException(
            status_code=400, 
            detail="La persona tiene 5 o más turnos cancelados en los últimos 6 meses"
        )
    
    # Convertir string de hora a objeto time
    hora_obj = datetime.strptime(turno.hora, "%H:%M").time()
    
    db_turno = models.Turno(
        fecha=turno.fecha,
        hora=hora_obj,
        persona_id=turno.persona_id
    )
    
    db.add(db_turno)
    db.commit()
    db.refresh(db_turno)
    return db_turno

def get_turnos(db: Session):
    return db.query(models.Turno).all()

def get_turno(db: Session, turno_id: int):
    return db.query(models.Turno).filter(models.Turno.id == turno_id).first()

def delete_turno(db: Session, turno_id: int):
    db_turno = get_turno(db, turno_id)
    if not db_turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    db.delete(db_turno)
    db.commit()
    return {"message": "Turno eliminado correctamente"}

def update_turno(db: Session, turno_id: int, turno: schemas.TurnoUpdate):
    db_turno = get_turno(db, turno_id)
    if not db_turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # Si se cambia la persona, verificar regla de negocio
    if turno.persona_id and turno.persona_id != db_turno.persona_id:
        turnos_cancelados = get_turnos_cancelados_recientes(db, turno.persona_id)
        if turnos_cancelados >= 5:
            raise HTTPException(
                status_code=400, 
                detail="La nueva persona tiene 5 o más turnos cancelados en los últimos 6 meses"
            )
    
    update_data = turno.dict(exclude_unset=True)
    
    # Convertir string de hora a objeto time si se proporciona
    if "hora" in update_data:
        update_data["hora"] = datetime.strptime(update_data["hora"], "%H:%M").time()
    
    for key, value in update_data.items():
        setattr(db_turno, key, value)
    
    db.commit()
    db.refresh(db_turno)
    return db_turno