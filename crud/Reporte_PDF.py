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



def generar_pdf_turnos_por_persona(dni: str, db):
    """
    Genera un PDF con todos los turnos de una persona según su DNI.
    Maneja internamente errores si no existe la persona o si no tiene turnos.
    """

    try:
        # Obtener los datos desde el CRUD
        reporte = CrudReporte.get_turnos_por_persona_dni(db, dni)

        if not reporte:
            raise HTTPException(status_code=404, detail=f"No se encontró una persona con DNI {dni}")

        if not hasattr(reporte, "turnos") or reporte.turnos is None:
            raise HTTPException(status_code=404, detail=f"No se pudieron obtener los turnos de la persona con DNI {dni}")

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
                text_alignment=Alignment.CENTERED,
            )
        )
        layout.add(
            Paragraph(
                f"Turnos de {reporte.nombre} (DNI {dni})",
                font_size=14,
                text_alignment=Alignment.CENTERED,
            )
        )
        layout.add(
            Paragraph(
                f"Cantidad total de turnos: {len(reporte.turnos)}",
                font_size=11,
                text_alignment=Alignment.CENTERED,
            )
        )
        layout.add(
            Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                font_size=9,
                text_alignment=Alignment.CENTERED,
            )
        )
        layout.add(Paragraph(" "))

        # --- Si no tiene turnos ---
        if not reporte.turnos:
            layout.add(Paragraph("La persona no tiene turnos registrados."))
        else:
            # Crear tabla con encabezados
            col_count = 4
            ancho_total = Decimal(520)
            col_widths = [ancho_total / Decimal(col_count)] * col_count

            table = FixedColumnWidthTable(
                number_of_rows=len(reporte.turnos) + 1,
                number_of_columns=col_count,
                column_widths=col_widths
            )

            # Encabezados
            encabezados = ["ID", "Fecha", "Hora", "Estado"]
            for header in encabezados:
                table.add(
                    TableCell(
                        Paragraph(header, font_color=X11Color("White"),
                                  font_size=12, text_alignment=Alignment.CENTERED),
                        background_color=HexColor("#1976D2")
                    )
                )

            # Filas de datos (centradas y alternadas)
            for i, turno in enumerate(reporte.turnos):
                bg_color = HexColor("#E3F2FD") if i % 2 == 0 else HexColor("#FFFFFF")
                table.add(TableCell(Paragraph(str(turno.id), text_alignment=Alignment.CENTERED), background_color=bg_color))
                table.add(TableCell(Paragraph(str(turno.fecha), text_alignment=Alignment.CENTERED), background_color=bg_color))
                table.add(TableCell(Paragraph(str(turno.hora), text_alignment=Alignment.CENTERED), background_color=bg_color))
                table.add(TableCell(Paragraph(turno.estado.capitalize(), text_alignment=Alignment.CENTERED), background_color=bg_color))

            layout.add(table)

        # --- Pie de página ---
        layout.add(Paragraph(" "))
        layout.add(
            Paragraph(
                "Sistema de Gestión de Turnos - SL UNLA LAB 2025",
                font_size=9,
                font_color=HexColor("#424242"),
                text_alignment=Alignment.RIGHT,
            )
        )

        # Guardar PDF
        carpeta_destino = "reportes_pdf"
        os.makedirs(carpeta_destino, exist_ok=True)
        nombre_archivo = f"turnos_persona_{dni}.pdf"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_completa, "wb") as f:
            PDF.dumps(f, doc)

        # Retornar el archivo listo para descargar
        return FileResponse(
            path=ruta_completa,
            media_type="application/pdf",
            filename=nombre_archivo,
        )

    except HTTPException as e:
        # Reenviamos el error si ya es una excepción de FastAPI
        raise e
    except Exception as e:
        # Cualquier otro error inesperado
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte PDF: {str(e)}")
    

def generar_pdf_personas_con_turnos_cancelados(db: Session, min_cancelados: int = 5):
    """
    Genera un PDF con las personas que tienen al menos 'min_cancelados' turnos cancelados.
    """
    try:
        # Obtener datos desde el CRUD normal
        personas = CrudReporte.get_personas_con_turnos_cancelados(db, min_cancelados)

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
                f"Personas con al menos {min_cancelados} turnos cancelados",
                font_size=14,
                text_alignment=Alignment.CENTERED
            )
        )
        layout.add(
            Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                font_size=10
            )
        )
        layout.add(Paragraph(" "))

        # 3️⃣ Validar si hay datos
        if not personas or len(personas) == 0:
            layout.add(
                Paragraph(
                    "⚠ No se encontraron personas con turnos cancelados en este período.",
                    font_color=HexColor("#D32F2F"),
                    font_size=12,
                    text_alignment=Alignment.CENTERED
                )
            )
        else:
            # Crear tabla con encabezados
            col_count = 4
            ancho_total = Decimal(520)
            col_widths = [ancho_total / Decimal(col_count)] * col_count

            if not col_widths or col_count == 0:
                raise HTTPException(status_code=500, detail="Error interno: tabla vacía o mal configurada")

            table = FixedColumnWidthTable(
                number_of_rows=len(personas) + 1,
                number_of_columns=col_count,
                column_widths=col_widths
            )

            # --- Encabezados ---
            encabezados = ["ID Persona", "Nombre", "Cancelados", "Turnos (Fecha y Hora)"]
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

            # --- Filas ---
            for persona in personas:
                turnos_texto = ", ".join(
                    [f"{t.fecha} {t.hora}" for t in persona.turnos_cancelados]
                ) if persona.turnos_cancelados else "-"

                table.add(TableCell(Paragraph(str(persona.id_usuario), text_alignment=Alignment.CENTERED)))
                table.add(TableCell(Paragraph(persona.nombre, text_alignment=Alignment.CENTERED)))
                table.add(TableCell(Paragraph(str(persona.cantidad_cancelados), text_alignment=Alignment.CENTERED)))
                table.add(TableCell(Paragraph(turnos_texto, text_alignment=Alignment.CENTERED)))

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

        # Guardar PDF
        carpeta_destino = "reportes_pdf"
        os.makedirs(carpeta_destino, exist_ok=True)
        nombre_archivo = f"personas_con_turnos_cancelados_min{min_cancelados}.pdf"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_completa, "wb") as f:
            PDF.dumps(f, doc)

        # Retornar archivo PDF
        return FileResponse(
            path=ruta_completa,
            media_type="application/pdf",
            filename=nombre_archivo
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")
