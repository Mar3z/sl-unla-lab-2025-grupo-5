from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from datetime import date, datetime, timedelta, time
import models
from schemas import Persona as SchPersona
from schemas import Turno as SchTurno
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno

# >>> REPORTES DE TURNOS <<<<

def get_turnos_por_fecha(db: Session, fecha: date):
    return db.query(models.Turno).filter(models.Turno.fecha == fecha).all()

def get_turnos_cancelados_mes_actual(db: Session):
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)
    
    if hoy.month == 12:
        fin_mes = date(hoy.year + 1, 1, 1) - timedelta(days=1)
    else:
        fin_mes = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    
    return db.query(models.Turno).filter(
        and_(
            models.Turno.estado == "cancelado",
            models.Turno.fecha >= inicio_mes,
            models.Turno.fecha <= fin_mes
        )
    ).all()

def get_turnos_por_persona_dni(db: Session, dni: str):
    persona = db.query(models.Persona).filter(models.Persona.dni == dni).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return db.query(models.Turno).filter(models.Turno.persona_id == persona.id).all()

def get_personas_con_turnos_cancelados(db: Session, min_cancelados: int = 5):

    subquery = select(
        models.Turno.persona_id,
        func.count(models.Turno.id).label('cantidad_cancelados')
    ).where(
        models.Turno.estado == "cancelado"
    ).group_by(
        models.Turno.persona_id
    ).having(
        func.count(models.Turno.id) >= min_cancelados
    ).subquery()
    
    resultados = db.query(
        models.Persona,
        subquery.c.cantidad_cancelados
    ).join(
        subquery, models.Persona.id == subquery.c.persona_id
    ).all()
    
    return resultados

def get_turnos_confirmados_periodo(db: Session, desde: date, hasta: date, skip: int = 0, limit: int = 5):
    """Obtiene turnos confirmados en un período con paginación"""
    return db.query(models.Turno).filter(
        and_(
            models.Turno.estado == "confirmado",
            models.Turno.fecha >= desde,
            models.Turno.fecha <= hasta
        )
    ).offset(skip).limit(limit).all()

def get_total_turnos_confirmados_periodo(db: Session, desde: date, hasta: date):
    """Obtiene el total de turnos confirmados en un período (para paginación)"""
    return db.query(models.Turno).filter(
        and_(
            models.Turno.estado == "confirmado",
            models.Turno.fecha >= desde,
            models.Turno.fecha <= hasta
        )
    ).count()


def get_personas_por_estado(db: Session, habilitada: bool):
    """Obtiene personas habilitadas o inhabilitadas"""
    return db.query(models.Persona).filter(models.Persona.habilitado == habilitada).all()