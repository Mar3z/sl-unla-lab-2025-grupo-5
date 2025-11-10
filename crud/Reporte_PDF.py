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
from datetime import date, datetime
import crud.Reporte as CrudReporte
import os
from decimal import Decimal


# GENERAR REPORTE PDF DE TURNOS POR FECHA
def generar_pdf_turnos_por_fecha(fecha: date, db: Session):
    try:
        reporte = CrudReporte.get_turnos_por_fecha(db, fecha)
        print(f"Generando PDF de turnos para la fecha {fecha}...")

        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)

        # Encabezado
        layout.add(
            Paragraph("SL - UNLA LAB 2025 - GRUPO 5", font_size=16,
                      font_color=HexColor("#1E88E5"), text_alignment=Alignment.CENTERED)
        )
        layout.add(
            Paragraph(f"Reporte de turnos del día {fecha.strftime('%d/%m/%Y')}",
                      font_size=14, text_alignment=Alignment.CENTERED)
        )
        layout.add(Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            font_size=10, text_alignment=Alignment.CENTERED
        ))
        layout.add(Paragraph(" "))

        if not reporte.turnos:
            layout.add(Paragraph("No hay turnos registrados en esta fecha."))
        else:
            table = FixedColumnWidthTable(
                number_of_rows=len(reporte.turnos) + 1, number_of_columns=4
            )

            # Encabezados
            for header in ["ID", "Hora", "Persona", "Estado"]:
                table.add(
                    TableCell(
                        Paragraph(header, font_color=X11Color("White"),
                                  font_size=12, text_alignment=Alignment.CENTERED),
                        background_color=HexColor("#1976D2")
                    )
                )

            # Filas con color alternado
            for i, turno in enumerate(reporte.turnos):
                bg_color = HexColor("#E3F2FD") if i % 2 == 0 else HexColor("#FFFFFF")

                table.add(TableCell(Paragraph(str(turno.id),
                                              text_alignment=Alignment.CENTERED), background_color=bg_color))
                table.add(TableCell(Paragraph(str(turno.hora),
                                              text_alignment=Alignment.CENTERED), background_color=bg_color))
                table.add(TableCell(Paragraph(turno.persona_nombre,
                                              text_alignment=Alignment.CENTERED), background_color=bg_color))
                table.add(TableCell(Paragraph(turno.estado.capitalize(),
                                              text_alignment=Alignment.CENTERED), background_color=bg_color))

            layout.add(table)

        # Pie de página
        layout.add(Paragraph(" "))
        layout.add(Paragraph("Sistema de Gestión de Turnos - SL UNLA LAB 2025",
                             font_size=9, font_color=HexColor("#424242"),
                             text_alignment=Alignment.RIGHT))

        # Guardar PDF
        carpeta_destino = "reportes_pdf"
        os.makedirs(carpeta_destino, exist_ok=True)
        nombre_archivo = f"reporte_turnos_{fecha}.pdf"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_completa, "wb") as f:
            PDF.dumps(f, doc)

        print(f"PDF generado correctamente: {ruta_completa}")

        return FileResponse(path=ruta_completa, media_type="application/pdf", filename=nombre_archivo)

    except Exception as e:
        print("ERROR en generar_pdf_turnos_por_fecha:", e)
        raise HTTPException(status_code=500, detail=str(e))


def generar_pdf_turnos_cancelados_mes_actual(db):
    #Genera un PDF con los turnos cancelados del mes actual, agrupados por persona.

    reporte = CrudReporte.get_turnos_cancelados_mes_actual(db)

    # Aseguramos que la estructura sea correcta
    if not hasattr(reporte, "turnos") or not reporte.turnos:
        reporte.turnos = []

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
            f"Turnos cancelados - {reporte.mes.capitalize()} {reporte.anio}",
            font_size=14,
            text_alignment=Alignment.CENTERED
        )
    )
    layout.add(
        Paragraph(
            f"Total de turnos cancelados: {reporte.cantidad}",
            font_size=11,
            text_alignment=Alignment.CENTERED
        )
    )
    layout.add(
        Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            font_size=9,
            text_alignment=Alignment.CENTERED
        )
    )
    layout.add(Paragraph(" "))

    # --- Si no hay datos ---
    filas_totales = sum(len(p.turnos) for p in reporte.turnos if hasattr(p, "turnos"))
    if filas_totales == 0:
        layout.add(Paragraph("No se registraron turnos cancelados en este mes."))
    else:
        # Crear tabla solo si hay filas válidas
        ancho_total = Decimal(520)
        col_count = 3
        col_widths = [ancho_total / Decimal(col_count)] * col_count

        # Número de filas = encabezado + filas de datos
        total_rows = filas_totales + 1

        table = FixedColumnWidthTable(
            number_of_rows=total_rows,
            number_of_columns=col_count,
            column_widths=col_widths
        )

        # --- Encabezados ---
        for header in ["Persona", "Fecha", "Hora"]:
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

        # --- Agregar filas de datos ---
        fila = 0
        for persona in reporte.turnos:
            if not hasattr(persona, "turnos") or not persona.turnos:
                continue
            for turno in persona.turnos:
                bg_color = HexColor("#E3F2FD") if fila % 2 == 0 else HexColor("#FFFFFF")
                table.add(
                    TableCell(
                        Paragraph(persona.nombre, text_alignment=Alignment.CENTERED),
                        background_color=bg_color
                    )
                )
                table.add(
                    TableCell(
                        Paragraph(str(turno.fecha), text_alignment=Alignment.CENTERED),
                        background_color=bg_color
                    )
                )
                table.add(
                    TableCell(
                        Paragraph(str(turno.hora), text_alignment=Alignment.CENTERED),
                        background_color=bg_color
                    )
                )
                fila += 1

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

    # --- Guardar PDF ---
    carpeta_destino = "reportes_pdf"
    os.makedirs(carpeta_destino, exist_ok=True)
    nombre_archivo = f"turnos_cancelados_{reporte.mes}_{reporte.anio}.pdf"
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

    with open(ruta_completa, "wb") as f:
        PDF.dumps(f, doc)

    return FileResponse(
        path=ruta_completa,
        media_type="application/pdf",
        filename=nombre_archivo
    )

