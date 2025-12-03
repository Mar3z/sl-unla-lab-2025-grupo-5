from fastapi.responses import FileResponse
from fastapi import HTTPException
from borb.pdf import Document, Page, PDF
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.color.color import HexColor, X11Color
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal
import crud.Reporte as CrudReporte
import os

# ──────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ──────────────────────────────────────────────

def _crear_doc_encabezado(titulo: str, subtitulo: str = ""):
    """Crea un documento PDF con el encabezado estándar."""
    doc = Document()
    page = Page()
    doc.add_page(page)
    layout = SingleColumnLayout(page)

    layout.add(Paragraph("SL - UNLA LAB 2025 - GRUPO 5",
                         font_size=16, font_color=HexColor("#1E88E5"),
                         text_alignment=Alignment.CENTERED))
    layout.add(Paragraph(titulo, font_size=14, text_alignment=Alignment.CENTERED))
    if subtitulo:
        layout.add(Paragraph(subtitulo, font_size=11, text_alignment=Alignment.CENTERED))
    layout.add(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                         font_size=9, text_alignment=Alignment.CENTERED))
    layout.add(Paragraph(" "))
    return doc, layout


def _crear_tabla(encabezados: list[str], filas: list[list[str]]):
    """Crea una tabla con estilo y filas alternadas."""
    if not encabezados:
        return Paragraph("⚠ No hay datos para mostrar.", font_color=HexColor("#D32F2F"))

    col_count = len(encabezados)
    ancho_total = Decimal(520)
    col_widths = [ancho_total / Decimal(col_count)] * col_count
    table = FixedColumnWidthTable(len(filas) + 1, col_count, col_widths)

    # Encabezados
    for header in encabezados:
        table.add(TableCell(
            Paragraph(header, font_color=X11Color("White"), font_size=12,
                      text_alignment=Alignment.CENTERED),
            background_color=HexColor("#1976D2"))
        )

    # Filas
    for i, fila in enumerate(filas):
        bg = HexColor("#E3F2FD") if i % 2 == 0 else HexColor("#FFFFFF")
        for celda in fila:
            table.add(TableCell(Paragraph(str(celda), text_alignment=Alignment.CENTERED),
                                background_color=bg))
    return table


def _pie_de_pagina(layout):
    """Agrega el pie de página común."""
    layout.add(Paragraph(" "))
    layout.add(Paragraph("Sistema de Gestión de Turnos - SL UNLA LAB 2025",
                         font_size=9, font_color=HexColor("#424242"),
                         text_alignment=Alignment.RIGHT))


def _guardar_y_retornar_pdf(doc: Document, nombre: str):
    """Guarda el PDF generado y devuelve el archivo listo para descargar."""
    carpeta = "reportes_pdf"
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "wb") as f:
        PDF.dumps(f, doc)
    return FileResponse(path=ruta, media_type="application/pdf", filename=nombre)

# ──────────────────────────────────────────────
# REPORTES PDF
# ──────────────────────────────────────────────

def generar_pdf_turnos_por_fecha(fecha: date, db: Session):
    """PDF con los turnos registrados en una fecha específica."""
    try:
        reporte = CrudReporte.get_turnos_por_fecha(db, fecha)
        doc, layout = _crear_doc_encabezado(f"Turnos del día {fecha.strftime('%d/%m/%Y')}")

        if not reporte.turnos:
            layout.add(Paragraph("No hay turnos registrados en esta fecha."))
        else:
            filas = [[t.id, t.hora, t.persona_nombre, t.estado.capitalize()] for t in reporte.turnos]
            layout.add(_crear_tabla(["ID", "Hora", "Persona", "Estado"], filas))

        _pie_de_pagina(layout)
        return _guardar_y_retornar_pdf(doc, f"turnos_fecha_{fecha}.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")


def generar_pdf_turnos_cancelados_mes_actual(db: Session):
    """PDF con los turnos cancelados del mes actual."""
    try:
        reporte = CrudReporte.get_turnos_cancelados_mes_actual(db)
        doc, layout = _crear_doc_encabezado(
            f"Turnos cancelados - {reporte.mes.capitalize()} {reporte.anio}",
            f"Total cancelados: {reporte.cantidad}"
        )

        filas = [
            [persona.nombre, t.fecha, t.hora]
            for persona in getattr(reporte, "turnos", [])
            for t in getattr(persona, "turnos", [])
        ]

        if not filas:
            layout.add(Paragraph("No se registraron turnos cancelados en este mes."))
        else:
            layout.add(_crear_tabla(["Persona", "Fecha", "Hora"], filas))

        _pie_de_pagina(layout)
        return _guardar_y_retornar_pdf(doc, f"turnos_cancelados_{reporte.mes}_{reporte.anio}.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")


def generar_pdf_turnos_por_persona(dni: str, db: Session):
    """PDF con los turnos de una persona según su DNI."""
    try:
        reporte = CrudReporte.get_turnos_por_persona_dni(db, dni)
        if not reporte:
            raise HTTPException(status_code=404, detail=f"No se encontró persona con DNI {dni}")

        doc, layout = _crear_doc_encabezado(
            f"Turnos de {reporte.nombre} (DNI {dni})",
            f"Total de turnos: {len(reporte.turnos)}"
        )

        if not reporte.turnos:
            layout.add(Paragraph("La persona no tiene turnos registrados."))
        else:
            filas = [[t.id, t.fecha, t.hora, t.estado.capitalize()] for t in reporte.turnos]
            layout.add(_crear_tabla(["ID", "Fecha", "Hora", "Estado"], filas))

        _pie_de_pagina(layout)
        return _guardar_y_retornar_pdf(doc, f"turnos_persona_{dni}.pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")
    
def generar_pdf_personas_con_turnos_cancelados(db: Session, min_cancelados: int = 5):
    """Genera un PDF con las personas que tienen al menos 'min_cancelados' turnos cancelados."""
    try:
        personas = CrudReporte.get_personas_con_turnos_cancelados(db, min_cancelados)
        doc, layout = _crear_doc_encabezado(
            f"Personas con al menos {min_cancelados} turnos cancelados"
        )

        if not personas:
            layout.add(Paragraph("No se encontraron personas con tantos turnos cancelados."))
        else:
            filas = [
                [
                    p.id_usuario,
                    p.nombre,
                    p.cantidad_cancelados,
                    ", ".join(f"{t.fecha} {t.hora}" for t in p.turnos_cancelados)
                ]
                for p in personas
            ]
            layout.add(_crear_tabla(["ID", "Nombre", "Cancelados", "Turnos (Fecha y Hora)"], filas))
            layout.add(Paragraph(f"Total: {len(personas)}", font_size=11,
                                 font_color=HexColor("#0D47A1"), text_alignment=Alignment.RIGHT))

        _pie_de_pagina(layout)
        return _guardar_y_retornar_pdf(doc, f"personas_cancelados_{min_cancelados}.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")
    

def generar_pdf_turnos_confirmados_periodo(db: Session, desde: date, hasta: date):
    """Genera un PDF con los turnos confirmados dentro de un rango de fechas."""
    try:
        reporte = CrudReporte.get_turnos_confirmados_periodo(db, desde, hasta)

        # Verificamos que reporte tenga datos válidos
        turnos = getattr(reporte, "turnos", reporte or [])
        if not isinstance(turnos, list):
            turnos = []

        titulo = f"Turnos confirmados entre {desde.strftime('%d/%m/%Y')} y {hasta.strftime('%d/%m/%Y')}"
        subtitulo = f"Total confirmados: {len(turnos)}" if turnos else ""
        doc, layout = _crear_doc_encabezado(titulo, subtitulo)

        if not turnos:
            layout.add(Paragraph("No se registraron turnos confirmados en este período."))
        else:
            filas = []
            for t in turnos:
                # Intentamos obtener el nombre de la persona de forma segura
                persona = getattr(t, "persona_nombre", None) or getattr(getattr(t, "persona", None), "nombre", "Sin asignar")
                filas.append([t.id, t.fecha, t.hora, persona, t.estado.capitalize()])

            layout.add(_crear_tabla(["ID", "Fecha", "Hora", "Persona", "Estado"], filas))

        _pie_de_pagina(layout)
        nombre = f"turnos_confirmados_{desde.strftime('%Y%m%d')}_{hasta.strftime('%Y%m%d')}.pdf"
        return _guardar_y_retornar_pdf(doc, nombre)

    except Exception as e:
        print(f"[ERROR PDF TURNOS CONFIRMADOS] {e}")  # te mostrará el problema real en consola
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")



def generar_pdf_estado_personas(db: Session, habilitada: bool):
    """Genera un PDF con las personas habilitadas o inhabilitadas."""
    try:
        personas = CrudReporte.get_personas_por_estado(db, habilitada)
        estado = "HABILITADAS" if habilitada else "INHABILITADAS"
        doc, layout = _crear_doc_encabezado(f"Personas {estado}")

        if not personas:
            layout.add(Paragraph(f"No hay personas {estado.lower()} en el sistema."))
        else:
            filas = [[p.id, p.nombre, p.dni] for p in personas]
            layout.add(_crear_tabla(["ID", "Nombre", "DNI"], filas))
            layout.add(Paragraph(f"Total: {len(personas)}", font_size=11,
                                 font_color=HexColor("#0D47A1"), text_alignment=Alignment.RIGHT))

        _pie_de_pagina(layout)
        return _guardar_y_retornar_pdf(doc, f"personas_{estado.lower()}_{datetime.now().strftime('%Y%m%d')}.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")