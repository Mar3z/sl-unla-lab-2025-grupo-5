# sl-unla-lab-2025-grupo-5

Bienvenidos, este el proyecto para la materia Seminario de Lenguajes (orientación Python), cursada 2025, Universidad Nacional de Lanús.
El trabajo pertenece al grupo 5, compuesto por los siguientes integrantes:
- Barreto Martín Ezequiel       @Mar3z
- Brandan Fabrizio              @fabriziobrandan-cpu
- Crespo Barreira Lourdes Noelia    @LourdesCrespo

# Instrucciones para levantar el proyecto
- Utilizar el comando "git clone https://github.com/Mar3z/sl-unla-lab-2025-grupo-5.git" para descargar el proyecto.
- Una vez descargado, dentro de su entorno virtual, ejecutar el comando "pip install -r requirements.txt" para descargar las dependencias necesarias.
- Ya descargadas las dependencias, ejecute el comando "fastapi dev main.py" para empezar el correr la API.
- Con la API ya corriendo, desde su navegar ingrese a la URL "127.0.0.1:8000" para corroborar que está funcionando.
- Y luego puede dirigirse a la URL "127.0.0.1:8000/docs" para empezar a hacer los tests correspondientes.

-------------------------------------------------------------------------------

# ABM PERSONAS

**Autores**: *Crespo Barreira Lourdes Noelia* @LourdesCrespo

### Tareas realizadas

* Configuración inicial de **FastAPI** + **SQLite** con **SQLAlchemy**.
* Creación del proyecto base con FastAPI.
* Configuración de la base de datos `turnos.db`.
* Definición del modelo **Persona** con los campos:

  * `id` (PK, autoincremental)
  * `nombre`
  * `email` (único)
  * `dni` (único)
  * `telefono`
  * `fecha_nacimiento`
  * `edad` (calculada automáticamente)
  * `habilitado` (por defecto `True`)

### Cambios y validaciones implementadas

* Cálculo automático de edad a partir de la fecha de nacimiento.
* Validación de fecha de nacimiento → no se permite una fecha futura.
* Email y DNI deben ser **únicos** → si se intenta duplicar, retorna **HTTP 400**.
* Manejo de errores controlado para evitar **Internal Server Error**.

### Endpoints implementados

1. **POST /personas** → Alta de persona (*responsable: LourdesCrespo*)
2. **GET /personas** → Listado de todas las personas (*responsable: LourdesCrespo*)
3. **GET /personas/{id}** → Búsqueda de persona por ID (*responsable: LourdesCrespo*)
4. **PUT /personas/{id}** → Actualización de persona (*responsable: LourdesCrespo*)
5. **DELETE /personas/{id}** → Baja de persona (*responsable: LourdesCrespo*)

           - Email y DNI deben ser únicos → en caso de duplicados, retorna error HTTP 400.
           - Manejo de errores controlado para evitar que el servidor se caiga (Internal Server Error).
---------------------------------------------------------------------------------------------



