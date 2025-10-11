from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import PDF
from borb.pdf import SingleColumnLayout
from borb.pdf import Paragraph

def generar_pdf(nombre_archivo: str):
    # Crear documento
    doc = Document()

    # Crear página
    page = Page()
    doc.add_page(page)

    # Layout de la página
    layout = SingleColumnLayout(page)

    # Agregar contenido
    layout.add(Paragraph("¡Hola! Este es un PDF generado con Borb."))
    layout.add(Paragraph("Podés añadir tablas, imágenes y más."))

    # Guardar PDF
    with open(nombre_archivo, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)

if __name__ == "__main__":
    generar_pdf("ejemplo.pdf")
    print("PDF generado: ejemplo.pdf")