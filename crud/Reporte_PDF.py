from fastapi.responses import FileResponse
from borb.pdf import Document, Page, PDF
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from datetime import date, datetime, timedelta, time
from collections import defaultdict
from models.Turno import Turno as Turno
from models.Persona import Persona as Persona
from schemas import Persona as SchPersona
from schemas import Turno as SchTurno
from schemas import Reporte as SchReporte
import crud.Reporte as CrudReporte
from fastapi import HTTPException
import os
import json
from dotenv import load_dotenv

def generar_pdf_turnos_por_fecha(fecha: date, db: Session):
    """ Genera un PDF con los turnos correspondientes a una fecha determinada."""

    # obtener el reporte JSON desde tu CRUD existente
    reporte = CrudReporte.get_turnos_por_fecha(db, fecha)

    # Crear documento PDF
    doc = Document()
    page = Page()
    doc.add_page(page)
    layout = SingleColumnLayout(page)

    layout.add(Paragraph(f"Reporte de turnos del día {fecha}"))
    layout.add(Paragraph(" "))

    # Agregar cada turno al PDF
    if not reporte.turnos:
        layout.add(Paragraph("No hay turnos registrados en esta fecha."))
    else:
        for turno in reporte.turnos:
            texto = f"ID: {turno.id} | Hora: {turno.hora} | Persona: {turno.persona_nombre} | Estado: {turno.estado}"
            layout.add(Paragraph(texto))

    # Guardar el PDF temporalmente
    nombre_archivo = f"reporte_turnos_{fecha}.pdf"
    with open(nombre_archivo, "wb") as f:
        PDF.dumps(f, doc)

    # Retornar el archivo generado
    return FileResponse(
        path=nombre_archivo,
        media_type="application/pdf",
        filename=nombre_archivo
    )