import pandas as pd
import os
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date

import crud.Reporte as CrudReporte

def generar_csv_turnos_por_fecha(db: Session, fecha: date):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_turnos_por_fecha(db, fecha)

    # En caso de no haber turnos esa fecha
    if not datos.turnos:
        raise HTTPException(status_code=404, detail=f"No hay turnos programados el día {fecha}")

    # Los formateamos
    datos_turnos = []
    for turno in datos.turnos:
        datos_turnos.append({
            'id': turno.id,
            'hora': turno.hora.strftime('%H:%M') if hasattr(turno.hora, 'strftime') else str(turno.hora),
            'persona_nombre': turno.persona_nombre,
            'estado': turno.estado
        })

    # Se crea un DataFrame con la información formateada
    df = pd.DataFrame(datos_turnos)
    df = df.sort_values(['hora'])

    # Modificamos la ruta de salida
    nombre_archivo = f"turnos_{fecha}.csv"
    carpeta_destino = Path("reportes_csv")
    carpeta_destino.mkdir(exist_ok=True) # Crea la carpeta si no existe
    ruta = carpeta_destino / nombre_archivo

    # Creamos el archivo CSV
    df.to_csv(ruta, index=False)

    return f"CSV guardado en: {ruta}"

def generar_csv_turnos_cancelados_por_mes(db: Session):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_turnos_cancelados_mes_actual(db)

    # En caso de no haber turnos cancelados este mes
    if not datos.turnos:
        raise HTTPException(status_code=404, detail=f"No hay turnos cancelados para {datos.mes} de {datos.anio}")

    # Los formateamos
    datos_turnos = []
    for persona_info in datos.turnos:
        for turno in persona_info.turnos:
            datos_turnos.append({
                'persona_id': persona_info.persona_id,
                'nombre_persona': persona_info.nombre,
                'turno_id': turno.id,
                'fecha': turno.fecha.strftime('%Y-%m-%d'),
                'hora': turno.hora.strftime('%H:%M') if hasattr(turno.hora, 'strftime') else str(turno.hora)
            })

    # Se crea un DataFrame con la información formateada
    df = pd.DataFrame(datos_turnos)

    # Modificamos la ruta de salida
    nombre_archivo = f"turnos_cancelados_{datos.mes}_{datos.anio}.csv"
    carpeta_destino = Path("reportes_csv")
    carpeta_destino.mkdir(exist_ok=True) # Crea la carpeta si no existe
    ruta = carpeta_destino / nombre_archivo

    # Creamos el archivo CSV
    df.to_csv(ruta, index=False)

    return f"CSV guardado en: {ruta}"

def generar_csv_turnos_por_persona(dni: str, db: Session):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_turnos_por_persona_dni(db, dni)

    # En caso de que esa persona no registre turnos
    if not datos.turnos:
        raise HTTPException(status_code=404, detail=f"No hay turnos programados para el usuario con el DNI {dni}")

    # Los formateamos
    datos_turnos = []
    for turno in datos.turnos:
        datos_turnos.append({
            'turno_id': turno.id,
            'fecha': turno.fecha.strftime('%Y-%m-%d'),
            'hora': turno.hora.strftime('%H:%M') if hasattr(turno.hora, 'strftime') else str(turno.hora),
            'estado': turno.estado
        })

    # Se crea un DataFrame con la información formateada
    df = pd.DataFrame(datos_turnos)
    df = df.sort_values(['turno_id'])

    # Modificamos la ruta de salida
    nombre_archivo = f"turnos_por_dni_{dni}.csv"
    carpeta_destino = Path("reportes_csv")
    carpeta_destino.mkdir(exist_ok=True) # Crea la carpeta si no existe
    ruta = carpeta_destino / nombre_archivo

    # Creamos el archivo CSV
    df.to_csv(ruta, index=False)

    return f"CSV guardado en: {ruta}"







