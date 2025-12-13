import pandas as pd
import os
from pathlib import Path
from fastapi import HTTPException, FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import date
from io import StringIO
import io
import csv

import crud.Reporte as CrudReporte

# Función auxiliar
def generar_reporte_html(titulo: str, df: pd.DataFrame, link_descarga: str):

    html_table = df.to_html(index=False, border=1)

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{titulo}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <p>Total de registros: {len(df)}</p>
            {html_table}
            <br>
            <a href="{link_descarga}">Descargar</a>
        </body>
        </html>
        """

    return HTMLResponse(content=html_content)

def descargar_reporte_csv(nombre_archivo: str, df: pd.DataFrame):

    # Crear un buffer en memoria para el CSV
    buffer = io.StringIO()
    
    # Escribir CSV al buffer
    df.to_csv(buffer, index=False, encoding='utf-8')
    
    # Obtener el contenido como string
    csv_content = buffer.getvalue()
    
    # Crear una respuesta de streaming
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"inline; filename={nombre_archivo}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )



def generar_csv_turnos_por_fecha(db: Session, fecha: date, descargar: bool = False):
    """Muestra los turnos de una fecha específica en formato HTML con botón de descarga."""
    try:
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
                'hora': turno.hora,
                'persona_nombre': turno.persona_nombre,
                'estado': turno.estado
            })

        # Strings importantes
        titulo = f"Turnos del día {fecha}"
        descarga = f"/reportes/csv/descargar-turnos-por-fecha?fecha={fecha}"

        # Se crea un DataFrame con la información formateada
        df = pd.DataFrame(datos_turnos)
        df = df.sort_values(['hora']) # Para ordenarlos por hora

        return generar_reporte_html(titulo, df, descarga)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la visualización: {str(e)}")

def descargar_csv_turnos_por_fecha(db: Session, fecha: date):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_turnos_por_fecha(db, fecha)

    # En caso de no haber turnos esa fecha
    if not datos.turnos:
        raise HTTPException(status_code=404, detail=f"No hay turnos programados el día {datos.fecha}")

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

    # Modificamos el nombre del archivo
    nombre_archivo = f"turnos_{fecha}.csv"

    return descargar_reporte_csv(nombre_archivo, df)

def generar_csv_turnos_cancelados_por_mes(db: Session):
    try:
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

        # Strings importantes
        titulo = f"Turnos cancelados {datos.mes} {datos.anio}"
        descarga = "/reportes/csv/descargar-turnos-cancelados-por-mes"

        # Se crea un DataFrame con la información formateada
        df = pd.DataFrame(datos_turnos)
        
        return generar_reporte_html(titulo, df, descarga)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la visualización: {str(e)}")

def descargar_csv_turnos_cancelados_por_mes(db: Session):
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

    # Modificamos el nombre del archivo
    nombre_archivo = f"turnos_cancelados_{datos.mes}_{datos.anio}.csv"
    
    return descargar_reporte_csv(nombre_archivo, df)

def generar_csv_turnos_por_persona(dni: str, db: Session):
    try:
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

        # Strings importantes
        titulo = f"Turnos DNI{dni}"
        descarga = f"/reportes/csv/descargar-turnos-por-persona?dni={dni}"

        # Se crea un DataFrame con la información formateada
        df = pd.DataFrame(datos_turnos)
        df = df.sort_values(['turno_id'])

        return generar_reporte_html(titulo, df, descarga)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la visualización: {str(e)}")

def descargar_csv_turnos_por_persona(dni: str, db: Session):
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

    # Modificamos el nombre del archivo
    nombre_archivo = f"turnos_{dni}.csv"

    return descargar_reporte_csv(nombre_archivo, df)

def generar_csv_turnos_cancelados(db: Session, min_cancelados: int = 5):
    try:
        # Importamos los datos que vamos a necesitar
        datos = CrudReporte.get_personas_con_turnos_cancelados(db, min_cancelados)

        # En caso de no haber personas con esa cantidad de turnos cancelados
        if not datos:
            raise HTTPException(status_code=404, detail=f"No hay personas con {min_cancelados} o más turnos cancelados")

        # Los formateamos
        datos_csv = []
        for persona in datos:
            datos_csv.append({
                'persona_id': persona.id_usuario,
                'nombre': persona.nombre,
                'total_cancelados': persona.cantidad_cancelados
            })

        # Strings importantes
        titulo = f"Personas con {min_cancelados} o más turnos cancelados"
        descarga = f"/reportes/csv/descargar-turnos-cancelados?min={min_cancelados}"

        # Se crea un DataFrame con la información formateada
        df = pd.DataFrame(datos_csv)

        return generar_reporte_html(titulo, df, descarga)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la visualización: {str(e)}")

def descargar_csv_turnos_cancelados(db: Session, min_cancelados: int = 5):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_personas_con_turnos_cancelados(db, min_cancelados)

    # En caso de no haber personas con esa cantidad de turnos cancelados
    if not datos:
        raise HTTPException(status_code=404, detail=f"No hay personas con {min_cancelados} o más turnos cancelados")

    # Los formateamos
    datos_csv = []
    for persona in datos:
        datos_csv.append({
            'persona_id': persona.id_usuario,
            'nombre': persona.nombre,
            'total_cancelados': persona.cantidad_cancelados
        })

    # Se crea un DataFrame con la información formateada
    df = pd.DataFrame(datos_csv)

    # Modificamos el nombre del archivo
    nombre_archivo = f"personas_con_{min_cancelados}_o_mas_cancelaciones.csv"

    return descargar_reporte_csv(nombre_archivo, df)

def generar_csv_turnos_confirmados_periodo(db: Session, desde: date, hasta: date):
    try:
        # Importamos los datos que vamos a necesitar
        datos = CrudReporte.get_turnos_confirmados_periodo(db, desde, hasta)

        # En caso de no haber turnos en ese periodo
        if not datos["turnos"]:
            raise HTTPException(status_code=404, detail=f"No hay turnos confirmados del {desde} hasta {hasta}")

        # Los formateamos
        datos_turnos = []
        for turno in datos["turnos"]:
            datos_turnos.append({
                'id': turno.id,
                'fecha': turno.fecha.strftime('%Y-%m-%d'),
                'hora': turno.hora.strftime('%H:%M') if hasattr(turno.hora, 'strftime') else str(turno.hora),
                'persona_id': turno.persona_id,
                'persona_nombre': turno.persona_nombre
            })

        # Strings importantes
        titulo = f"Turnos confirmados del {desde} al {hasta}"
        descarga = f"/reportes/csv/descargar-turnos-confirmados?desde={desde}&hasta={hasta}"

        # Se crea un DataFrame con la información formateada
        df = pd.DataFrame(datos_turnos)
        df = df.sort_values(['fecha','hora'])

        return generar_reporte_html(titulo, df, descarga)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la visualización: {str(e)}")

    

def descargar_csv_turnos_confirmados_periodo(db: Session, desde: date, hasta: date):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_turnos_confirmados_periodo(db, desde, hasta)

    # En caso de no haber turnos en ese periodo
    if not datos["turnos"]:
        raise HTTPException(status_code=404, detail=f"No hay turnos confirmados del {desde} hasta {hasta}")

    # Los formateamos
    datos_turnos = []
    for turno in datos["turnos"]:
        datos_turnos.append({
            'id': turno.id,
            'fecha': turno.fecha.strftime('%Y-%m-%d'),
            'hora': turno.hora.strftime('%H:%M') if hasattr(turno.hora, 'strftime') else str(turno.hora),
            'persona_id': turno.persona_id,
            'persona_nombre': turno.persona_nombre
        })

    # Se crea un DataFrame con la información formateada
    df = pd.DataFrame(datos_turnos)
    df = df.sort_values(['fecha','hora'])

    # Modificamos la ruta de salida
    nombre_archivo = f"turnos_confirmados_{desde}_{hasta}.csv"

    return descargar_reporte_csv(nombre_archivo, df)

def generar_csv_personas_por_estado(db: Session, habilitada: bool):
    try:
        # Importamos los datos que vamos a necesitar
        datos = CrudReporte.get_personas_por_estado(db, habilitada)

        # Variable con el estado
        estado = "habilitadas" if habilitada else "no habilitadas"

        # En caso de no haber personas con ese estado
        if not datos:
            raise HTTPException(status_code=404, detail=f"No hay personas en estado habilitado={habilitada}")

        # Los formateamos
        personas = []
        for persona in datos:
            personas.append({
                'id': persona.id,
                'nombre': persona.nombre
            })

        # Strings importantes
        titulo = f"Personas {estado}"
        descarga = f"/reportes/csv/descargar-estado-personas?habilitada={habilitada}"

        # Se crea un DataFrame con la información formateada
        df = pd.DataFrame(personas)
        df = df.sort_values(['id'])

        return generar_reporte_html(titulo, df, descarga)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la visualización: {str(e)}")

def descargar_csv_personas_por_estado(db: Session, habilitada: bool):
    # Importamos los datos que vamos a necesitar
    datos = CrudReporte.get_personas_por_estado(db, habilitada)

    # En caso de no haber personas con ese estado
    if not datos:
        raise HTTPException(status_code=404, detail=f"No hay personas en estado habilitado={habilitada}")

    # Los formateamos
    personas = []
    for persona in datos:
        personas.append({
            'id': persona.id,
            'nombre': persona.nombre
        })

    # Se crea un DataFrame con la información formateada
    df = pd.DataFrame(personas)
    df = df.sort_values(['id'])

    # Modificamos el nombre del archivo
    nombre_archivo = "personas_habilitadas.csv" if habilitada else "personas_no_habilitadas.csv"

    return descargar_reporte_csv(nombre_archivo, df)




