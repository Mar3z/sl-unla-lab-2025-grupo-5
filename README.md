# sl-unla-lab-2025-grupo-5

Bienvenidos, este el proyecto para la materia Seminario de Lenguajes (orientación Python), cursada 2025, Universidad Nacional de Lanús.
El trabajo pertenece al grupo 5, compuesto por los siguientes integrantes:
- Barreto Martín Ezequiel       @Mar3z
- Brandan Fabrizio              @fabriziobrandan-cpu
- Crespo Barreira Lourdes Noelia    @LourdesCrespo

**HITO 1: Link al video en YouTube** https://youtu.be/LxFqV9-48NE
**HITO 2: Link al video:**

**Link al Drive con las postman collection** https://drive.google.com/drive/folders/1dolAP98gcWkMu7YS27ySt-flRty8snt6?usp=sharing

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
* El nombre no puede estar vacio y no puede contener numeros.
* El DNI solo puede ser de 8 digitos y no puede ser negativo
* Manejo de errores controlado para evitar **Internal Server Error**.

### Endpoints implementados

1. **POST /personas** → Alta de persona (*responsable: LourdesCrespo*)
2. **GET /personas** → Listado de todas las personas (*responsable: LourdesCrespo*)
3. **GET /personas/{id}** → Búsqueda de persona por ID (*responsable: LourdesCrespo*)
4. **PUT /personas/{id}** → Actualización de persona (*responsable: LourdesCrespo*)
5. **DELETE /personas/{id}** → Baja de persona (*responsable: LourdesCrespo*)

           - Email y DNI deben ser únicos → en caso de duplicados, retorna error HTTP 400.
           - Manejo de errores controlado para evitar que el servidor se caiga (Internal Server Error).
           - El nombre no puede estar vacio y no puede contener numeros.
           - El DNI solo puede ser de 8 digitos y no puede ser negativo
---------------------------------------------------------------------------------------------

# ABM TURNOS
 - Realizado por Martín Barreto -

### TAREAS REALIZADAS
* Implementación y creación de la clase *TURNOS*
* Creación de los métodos para crear, listar, buscar y modificar turnos
* Atributos implementados a la clase:
  - 'id' (primary_key)
  - 'fecha'
  - 'hora'
  - 'persona_id' (Crea la conexión con la clase Persona)
  - 'estado' (Por defecto se crea como 'pendiente')

### ENDPOINT
 1. **POST (/turnos)** -> Crea un nuevo turno
 2. **GET (/turnos)** -> Lista todos los turnos
 3. **GET (/turnos/{id})** -> Obtiene un turno a través de su id
 4. **UPDATE (/turnos/{id})** -> Modifica un turno a través de su id
 5. **DELETE (/turnos/{id})** -> Elimina un turno a través de su id

### VALIDACIONES REALIZADAS
          - La fecha del turno no puede ser anterior a la fecha actual
          - El horario del turno no puede exceder el rango horario del negocio
          - No se le puede asignar un turno a un usuario que registre 5 turnos o más cancelados en los últimos 6 meses
          - No se puede asignar un estado que no sea 'pendiente', 'cancelado', 'confirmado' o 'asistido'

---------------------------------------------------------------------------------------------

# CALCULO DE TURNOS DISPONIBLES
 - Realizado por Fabrizio Brandan -

### TAREAS REALIZADAS
 * Implementación del endpoint para el cálculo dinámico de turnos disponibles
 * Definición del rango horario de turnos posibles: de 09:00 a 17:00, en intervalos de 30 minutos
 * Consulta a la base de datos para verificar turnos ocupados y cancelados
 * Implementación de la lógica que retorna únicamente los turnos libres en base a la fecha solicitada
 * Manejo de errores para fechas inválidas o con formato incorrecto

### ENDPOINT
 **GET (/turnos-disponibles?fecha=YYYY-MM-DD)** -> Retorna los horarios disponibles para la fecha indicada

### VALIDACIONES REALIZADAS
          - Solo se permiten fechas en formato YYYY-MM-DD
          - Los turnos disponibles son aquellos que no han sido asignados o que tienen estado 'cancelado'
          - Si un turno está tomado, no aparece en la respuesta
          - La consulta devuelve todos los horarios en intervalos de 30 minutos que aún estén libres
          - En caso de que no haya horarios disponibles, se retorna una lista vacía en formato JSON

---------------------------------------------------------------------------------------------------

### Implementación de la parte D del trabajo práctico: gestión de estado de turno.
 - Realizado por LourdesCrespo - 

### Cambios realizados
- Agregadas funciones `cancelar_turno` y `confirmar_turno` en `crud.py`.
- Nuevos endpoints `PUT /turnos/{id}/cancelar` y `PUT /turnos/{id}/confirmar` en `main.py`.
- Se restringió `update_turno` para que no permita modificar el campo `estado`.

### Reglas de negocio aplicadas
- No se puede modificar un turno ya cancelado o asistido.
- No se pueden eliminar ni cancelar turnos asistidos.
- Turnos cancelados liberan el horario (eliminación lógica).

### Testing
Se realizaron pruebas en Postman verificando:
- Cancelación correcta de turno pendiente.
- Confirmación correcta de turno pendiente.
- Errores adecuados al cancelar/confirmar turnos ya cancelados o asistidos.
  
---------------------------------------------------------------------------------------------

# GENERACIÓN DE REPORTES
 - Realizado por Martín Barreto - 

### Endpoints implementados

1. **GET /reportes/turnos-por-fecha** → Trae todos los turnos de una fecha específica (La fecha se indica como query param en formato "YYYY-MM-DD")
2. **GET /reportes/turnos-cancelados-por-mes** → Trae todos los turnos cancelados del mes actual
3. **GET /reportes/turnos-por-persona** → Trae todos los turnos de una persona específica (La persona se indica mediante su DNI a través de una query param)
4. **GET /reportes/turnos-cancelados** → Devuelve los usuarios con una cantidad determinada de turnos cancelados (La cantidad de turnos se indica por parámetro)
5. **GET /reportes/turnos-confirmados** → Devuelve los turnos confirmados en un periodo de tiempo determinado (El periodo se indica por parámetro con la fecha de inicio y la fecha de fin)
6. **GET /reportes/estado-personas** → Devuelve los usuarios según su estado si está habilitado o no(Se indica el estado por parámetro)

