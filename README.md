# sl-unla-lab-2025-grupo-5

Bienvenidos, este el proyecto para la materia Seminario de Lenguajes (orientación Python), cursada 2025, Universidad Nacional de Lanús.
El trabajo pertenece al grupo 5, compuesto por los siguientes integrantes:
- Barreto Martín Ezequiel       @Mar3z
- Brandan Fabrizio              @fabriziobrandan-cpu
- Crespo Barreira Lourdes Noelia    @LourdesCrespo
- Arriola Natalia               @nataliaarriola

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

------------------------------------------------------------------------------------
           - Email y DNI deben ser únicos → en caso de duplicados, retorna error HTTP 400.
           - Manejo de errores controlado para evitar que el servidor se caiga (Internal Server Error).
