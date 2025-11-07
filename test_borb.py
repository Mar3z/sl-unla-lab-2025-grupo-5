from borb.pdf import Document, Page, PDF
try:
    from borb.pdf.canvas.layout.page_layout.single_column_layout import SingleColumnLayout
except ModuleNotFoundError:
    from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph

# Crear documento
doc = Document()

# Crear y agregar página
page = Page()
doc.add_page(page)

# Crear layout
layout = SingleColumnLayout(page)

# Agregar texto simple
layout.add(Paragraph("Borb 2.1.15 funciona correctamente holi!"))

# Guardar el PDF correctamente con la clase PDF
with open("prueba_borb.pdf", "wb") as archivo:
    PDF.dumps(archivo, doc)

print("PDF generado correctamente: prueba_borb.pdf")
