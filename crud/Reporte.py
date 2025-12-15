from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from datetime import date, datetime, timedelta, time
from collections import defaultdict
from models.Turno import Turno as Turno
from models.Persona import Persona as Persona
from schemas import Persona as SchPersona
from schemas import Turno as SchTurno
from schemas import Reporte as SchReporte
import crud.Persona as CrudPersona
from fastapi import HTTPException
import os
import json
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno

# >>> REPORTES DE TURNOS <<<<

def get_turnos_por_fecha(db: Session, fecha: date):
    turnos = db.query(Turno).filter(Turno.fecha == fecha).all()
    
    turnos_por_fecha = SchReporte.TurnosPorFecha(
        fecha=fecha,
        turnos=[SchReporte.TurnosSinFecha(
            id=t.id,
            hora=t.hora,
            persona_nombre=t.persona.nombre,
            estado=t.estado
        ) for t in turnos
        ]
    )
    return turnos_por_fecha

def get_turnos_cancelados_mes_actual(db: Session):
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)
    
    if hoy.month == 12:
        fin_mes = date(hoy.year + 1, 1, 1) - timedelta(days=1)
    else:
        fin_mes = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    
    turnos = db.query(Turno).join(Persona).filter(
        and_(
            Turno.estado == "cancelado",
            Turno.fecha >= inicio_mes,
            Turno.fecha <= fin_mes
        )
    ).all()

    # Un diccionario para devolver el mes por el nombre
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    # Agrupar turnos por id de persona
    turnos_por_persona = {}
    for t in turnos:
        persona_id = t.persona_id
        if persona_id not in turnos_por_persona:
            turnos_por_persona[persona_id] = {'persona': t.persona, 'turnos': []}
        turnos_por_persona[persona_id]['turnos'].append(t)

    turnos_cancelados = []
    for persona_id, dato in turnos_por_persona.items():
        persona = dato['persona']
        turnos_basicos = [
            SchReporte.TurnoCanceladoInfoBasico(
                id=t.id,
                fecha=t.fecha,
                hora=t.hora
            ) for t in dato['turnos']
        ]
    
        turnos_cancelados.append(SchReporte.TurnoCanceladoInfo(
            persona_id=persona_id,
            nombre=persona.nombre,
            turnos=turnos_basicos
        ))

    return SchReporte.CanceladosMesEnCurso(
        anio = hoy.year,
        mes = meses[hoy.month],
        cantidad = len(turnos),
        turnos = turnos_cancelados
    )

def get_turnos_por_persona_dni(db: Session, dni: str):
    persona = db.query(Persona).filter(Persona.dni == dni).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    turnos = db.query(Turno).filter(Turno.persona_id == persona.id).all()

    turnos_formateados=[]
    for t in turnos:
        turnos_formateados.append(SchReporte.TurnoInfoBasica(id=t.id, fecha=t.fecha, hora=t.hora, estado=t.estado))

    return SchReporte.TurnosPorPersona(id_persona=persona.id, nombre=persona.nombre, turnos=turnos_formateados)

def get_personas_con_turnos_cancelados(db: Session, min_cancelados: int = 5):

    subquery = select(
        Turno.persona_id,
        func.count(Turno.id).label('cantidad_cancelados')
    ).where(
        Turno.estado == "cancelado"
    ).group_by(
        Turno.persona_id
    ).having(
        func.count(Turno.id) >= min_cancelados
    ).subquery()
    
    resultados = db.query(
        Persona,
        subquery.c.cantidad_cancelados
    ).join(
        subquery, Persona.id == subquery.c.persona_id
    ).all()
     
    response = []
    for persona, cant_cancelados in resultados:
        turnos = [t for t in get_turnos_por_persona_dni(db, CrudPersona.get_persona(db, persona.id).dni).turnos if t.estado == 'cancelado']   
        turnos_formateados=[]
        for t in turnos:
                turnos_formateados.append(SchReporte.TurnoCanceladoInfoBasico(
                    id=t.id,
                    fecha=t.fecha, 
                    hora=t.hora
                ))
        response.append(SchReporte.PersonasConTurnosCancelados(
            id_usuario=persona.id,
            nombre=CrudPersona.get_persona(db, persona.id).nombre,
            cantidad_cancelados=cant_cancelados,
            turnos_cancelados=turnos_formateados
        ))
    
    return response

def get_turnos_confirmados_periodo(db: Session, desde: date, hasta: date, skip: int = 0, limit: int = 5, pagina: int = 1):
    """Obtiene turnos confirmados en un período con paginación"""

    if desde > hasta:
        raise HTTPException(status_code=400, detail="La fecha 'desde' no puede ser mayor que 'hasta'")
    
    # Calcular skip para paginación
    registros_por_pagina = 5
    skip = (pagina - 1) * registros_por_pagina
    
    # Obtener datos paginados
    turnos = db.query(Turno).filter(
        and_(
            Turno.estado == "confirmado",
            Turno.fecha >= desde,
            Turno.fecha <= hasta
        )
    ).offset(skip).limit(limit).all()
    total = get_total_turnos_confirmados_periodo(db, desde, hasta)
    total_paginas = (total + registros_por_pagina - 1) // registros_por_pagina

    turnos_formateados = [SchReporte.TurnoConfirmado(
        id = turno.id,
        fecha = turno.fecha,
        hora = turno.hora,
        persona_id = turno.persona.id,
        persona_nombre = turno.persona.nombre
    )for turno in turnos]
    
    return {
        "turnos": turnos_formateados,
        "paginacion": {
            "pagina_actual": pagina,
            "total_paginas": total_paginas,
            "total_turnos": total,
            "turnos_por_pagina": registros_por_pagina
        }
    }

def get_total_turnos_confirmados_periodo(db: Session, desde: date, hasta: date):
    """Obtiene el total de turnos confirmados en un período (para paginación)"""
    return db.query(Turno).filter(
        and_(
            Turno.estado == "confirmado",
            Turno.fecha >= desde,
            Turno.fecha <= hasta
        )
    ).count()


def get_personas_por_estado(db: Session, habilitada: bool):

    personas = db.query(Persona).filter(Persona.habilitado == habilitada).all()

    personas_formateado = [
        SchReporte.PersonaPorEstado(
            id=p.id,
            nombre=p.nombre,
            dni=p.dni
        )
        for p in personas
    ]

    return personas_formateado
