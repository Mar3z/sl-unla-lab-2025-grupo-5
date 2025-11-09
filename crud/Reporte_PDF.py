from fastapi.responses import FileResponse
from borb.pdf import Document, Page, PDF
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.color.color import HexColor, X11Color
from sqlalchemy.orm import Session
from datetime import date, datetime
import crud.Reporte as CrudReporte
import os

def generar_pdf_turnos_por_fecha(fecha: date, db: Session):
    """Genera un PDF con formato visual para los turnos de una fecha."""

    # Obtener el reporte desde el CRUD existente
    reporte = CrudReporte.get_turnos_por_fecha(db, fecha)

    # Crear documento PDF
    doc = Document()
    page = Page()
    doc.add_page(page)
    layout = SingleColumnLayout(page)

    # --- Encabezado ---
    layout.add(
        Paragraph(
            "SL - UNLA LAB 2025 - GRUPO 5",
            font_size=16,
            font_color=HexColor("#1E88E5"),
            text_alignment=Alignment.CENTERED
        )
    )
    layout.add(
        Paragraph(
            f"Reporte de turnos del día {fecha.strftime('%d/%m/%Y')}",
            font_size=14,
            text_alignment=Alignment.CENTERED
        )
    )
    layout.add(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", font_size=10))
    layout.add(Paragraph(" "))

    # --- Si no hay turnos ---
    if not reporte.turnos:
        layout.add(Paragraph("No hay turnos registrados en esta fecha."))
    else:
        # --- Crear tabla con encabezados ---
        table = FixedColumnWidthTable(number_of_rows=len(reporte.turnos) + 1, number_of_columns=4)

        # Encabezados de tabla
        encabezados = ["ID", "Hora", "Persona", "Estado"]
        for header in encabezados:
            table.add(
                TableCell(
                    Paragraph(
                        header,
                        font_color=X11Color("White"),
                        font_size=12,
                        text_alignment=Alignment.CENTERED
                    ),
                    background_color=HexColor("#1976D2")
                )
            )

        # Filas de datos (centradas)
        for turno in reporte.turnos:
            table.add(
                TableCell(
                    Paragraph(str(turno.id), font_size=11, text_alignment=Alignment.CENTERED)
                )
            )
            table.add(
                TableCell(
                    Paragraph(str(turno.hora), font_size=11, text_alignment=Alignment.CENTERED)
                )
            )
            table.add(
                TableCell(
                    Paragraph(turno.persona_nombre, font_size=11, text_alignment=Alignment.CENTERED)
                )
            )
            table.add(
                TableCell(
                    Paragraph(turno.estado.capitalize(), font_size=11, text_alignment=Alignment.CENTERED)
                )
            )

        layout.add(table)

    # --- Pie de página ---
    layout.add(Paragraph(" "))
    layout.add(
        Paragraph(
            "Sistema de Gestión de Turnos - SL UNLA LAB 2025",
            font_size=9,
            font_color=HexColor("#424242"),
            text_alignment=Alignment.RIGHT
        )
    )

    # Guardar PDF en carpeta
    carpeta_destino = "reportes_pdf"
    os.makedirs(carpeta_destino, exist_ok=True)
    nombre_archivo = f"reporte_turnos_{fecha}.pdf"
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

    with open(ruta_completa, "wb") as f:
        PDF.dumps(f, doc)

    # Retornar archivo
    return FileResponse(
        path=ruta_completa,
        media_type="application/pdf",
        filename=nombre_archivo
    )
