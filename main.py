from fastapi import FastAPI, Depends,HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal,engine,Base, get_db  #Me aseguro de que exista database.py con SessionLocal
from models.Turno import Turno as Turno
from models.Persona import Persona as Persona
from schemas import Persona as SchPersona
from schemas import Turno as SchTurno
from schemas import Reporte as SchReporte
from crud import Persona as CrudPersona
from crud import Turno as CrudTurno
from crud import Reporte as CrudReporte
from datetime import date, datetime, time, timedelta
from sqlalchemy.exc import IntegrityError
from typing import List

#Creo tablas
Base.metadata.create_all(bind=engine)
app = FastAPI(title="SL-UNLA-LAB-2025-GRUPO-5")

@app.get("/")
def inicio():
    return {"mensaje": "SL-UNLA-LAB-2025-GRUPO-5"}

# ----- ENDPOINTS DE PERSONAS (CRUD) -----

# Crear persona / POST
@app.post("/personas", response_model=SchPersona.Persona, tags=["Persona"])
def crear_persona(persona: SchPersona.PersonaCreate, db: Session = Depends(get_db)):
    return CrudPersona.create_persona(db, persona)

# Obtener todas las personas / GET
@app.get("/personas", response_model=list[SchPersona.Persona], tags=["Persona"])
def listar_personas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CrudPersona.get_personas(db, skip, limit)

# Obtener persona por ID / GET
@app.get("/personas/{persona_id}", response_model=SchPersona.Persona, tags=["Persona"])
def obtener_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = CrudPersona.get_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

# Actualizar personas por id / PUT
@app.put("/personas/{persona_id}", response_model=SchPersona.Persona, tags=["Persona"])
def actualizar_persona(persona_id: int, persona: SchPersona.PersonaUpdate, db: Session = Depends(get_db)):
    return CrudPersona.update_persona(db, persona_id, persona)

# Eliminar personas por id/ DELETE
@app.delete("/personas/{persona_id}", tags=["Persona"])
def eliminar_persona(persona_id: int, db: Session = Depends(get_db)):
    return CrudPersona.delete_persona(db, persona_id)

# >>> Endpoints de turnos <<<

@app.post("/turnos", response_model=SchTurno.Turno, status_code=201, tags=["Turnos"])
def crear_turno(turno: SchTurno.TurnoCreate, db: Session = Depends(get_db)):
    return CrudTurno.create_turno(db, turno)

@app.get("/turnos", response_model=list[SchTurno.Turno], tags=["Turnos"])
def listar_turnos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CrudTurno.get_turnos(db)

@app.get("/turnos/{turno_id}", response_model=SchTurno.Turno, tags=["Turnos"])
def obtener_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = CrudTurno.get_turno(db, turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return turno

@app.delete("/turnos/{turno_id}", tags=["Turnos"])
def eliminar_turno(turno_id: int, db: Session = Depends(get_db)):
    return CrudTurno.delete_turno(db, turno_id)

@app.put("/turnos/{turno_id}", response_model=SchTurno.Turno, tags=["Turnos"])
def update_turno(turno_id: int, turno_update: SchTurno.TurnoUpdate, db: Session = Depends(get_db)):
    return CrudTurno.update_turno(db, turno_id, turno_update)

@app.get("/turnos-disponibles", tags=["Turnos"])
def turnos_disponibles(fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD"), db: Session = Depends(get_db)):
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Debe ser YYYY-MM-DD")
    
    return CrudTurno.get_turnos_disponibles(db, fecha_obj)

# >>> Endpoints de gestion de estado de turno <<< (PARTE D)

@app.put("/turnos/{turno_id}/cancelar", response_model=SchTurno.Turno)
def cancelar_turno_endpoint(turno_id: int, db: Session = Depends(get_db)):
    return CrudTurno.cancelar_turno(db, turno_id)

@app.put("/turnos/{turno_id}/confirmar", response_model=SchTurno.Turno)
def confirmar_turno_endpoint(turno_id: int, db: Session = Depends(get_db)):
    return CrudTurno.confirmar_turno(db, turno_id)

# >>> Endpoints de reportes <<<
@app.get("/reportes/turnos-por-fecha", response_model=list[SchReporte909.TurnoInfo], tags=["Reportes"])
def reporte_turnos_por_fecha(fecha: date, db: Session = Depends(get_db)):
    turnos = CrudReporte.get_turnos_por_fecha(db, fecha)
    return turnos

@app.get("/reportes/turnos-cancelados-por-mes", response_model=SchReporte.CanceladosMesEnCurso, tags=["Reportes"])
def reporte_turnos_cancelados_mes_actual(db: Session = Depends(get_db)):
    turnos_cancelados = CrudReporte.get_turnos_cancelados_mes_actual(db)
    response = SchReporte.CanceladosMesEnCurso(
        anio=turnos_cancelados["anio"], 
        mes=turnos_cancelados["mes"], 
        cantidad=turnos_cancelados["cantidad"], 
        turnos=turnos_cancelados["turnos"])
    return response

@app.get("/reportes/turnos-por-persona", response_model=list[SchTurno.Turno], tags=["Reportes"])
def reporte_turnos_por_persona(dni: str, db: Session = Depends(get_db)): 
    
    if not dni.isdigit() or len(dni) != 8:
        raise HTTPException(status_code=400, detail="El DNI debe tener 8 dígitos numéricos")

    turnos = CrudReporte.get_turnos_por_persona_dni(db, dni)
    return turnos

@app.get("/reportes/turnos-cancelados", tags=["Reportes"])
def reporte_personas_con_turnos_cancelados(min: int = 5, db: Session = Depends(get_db)):
    if min < 0:
        raise HTTPException(status_code=400, detail="El mínimo no puede ser negativo")
    
    resultados = CrudReporte.get_personas_con_turnos_cancelados(db, min)
    
    # Formatear la respuesta
    respuesta = []
    for persona, cantidad_cancelados in resultados:
        persona_dict = SchPersona.from_orm(persona).dict()
        persona_dict["cantidad_cancelados"] = cantidad_cancelados
        
        # Obtener los turnos cancelados de esta persona
        turnos_cancelados = CrudReporte.get_turnos_por_persona_dni(db, persona.dni)
        turnos_cancelados = [t for t in turnos_cancelados if t.estado == "cancelado"]
        
        persona_dict["turnos_cancelados"] = [
            {
                "id": turno.id,
                "fecha": turno.fecha,
                "hora": turno.hora,
                "estado": turno.estado
            }
            for turno in turnos_cancelados
        ]
        
        respuesta.append(persona_dict)
    
    return respuesta

@app.get("/reportes/turnos-confirmados", tags=["Reportes"])
def reporte_turnos_confirmados_periodo(desde: date, hasta: date, pagina: int = 1, db: Session = Depends(get_db)):

    if desde > hasta:
        raise HTTPException(status_code=400, detail="La fecha 'desde' no puede ser mayor que 'hasta'")
    
    # Calcular skip para paginación
    registros_por_pagina = 5
    skip = (pagina - 1) * registros_por_pagina
    
    # Obtener datos paginados
    turnos = CrudReporte.get_turnos_confirmados_periodo(db, desde, hasta, skip, registros_por_pagina)
    total = CrudReporte.get_total_turnos_confirmados_periodo(db, desde, hasta)
    total_paginas = (total + registros_por_pagina - 1) // registros_por_pagina
    
    return {
        "turnos": turnos,
        "paginacion": {
            "pagina_actual": pagina,
            "total_paginas": total_paginas,
            "total_turnos": total,
            "turnos_por_pagina": registros_por_pagina
        }
    }

@app.get("/reportes/estado-personas", response_model=list[SchPersona.Persona], tags=["Reportes"])
def reporte_personas_por_estado(habilitada: bool, db: Session = Depends(get_db)):
    """Obtiene personas habilitadas o inhabilitadas para sacar turnos"""
    personas = CrudReporte.get_personas_por_estado(db, habilitada)
    return personas