# sl-unla-lab-2025-grupo-5

Bienvenidos, este el proyecto para la materia Seminario de Lenguajes (orientación Python), cursada 2025, Universidad Nacional de Lanús.
El trabajo pertenece al grupo 5, compuesto por los siguientes integrantes:
- Barreto Martín Ezequiel       @Mar3z
- Brandan Fabrizio              @fabriziobrandan-cpu
- Crespo Barreira Lourdes Noelia    @LourdesCrespo
- Arriola Natalia               @nataliaarriola


ABM PERSONAS: - Crespo Barreira Lourdes Noelia    @LourdesCrespo
Tareas realizadas:
    - Incluye la configuración inicial de FastAPI + SQLite con SQLAlchemy y la definición del modelo Persona.
    - Cambios realizados:
        - Creación del proyecto base con FastAPI.
        - Configuración de la base de datos SQLite (turnos.db) y SQLAlchemy.
        - Creación del modelo 'Persona' con los siguientes campos:
           - id (PK, autoincremental)
           - nombre
           - email (único)
           - dni (único)
           - telefono
           - fecha_nacimiento
           - edad (calculada automáticamente)
           - habilitado (por defecto True)
        - Creación de endpoints:
           - POST /personas → alta de persona
           - GET /personas → listado de todas las personas
           - GET /personas/{id} → búsqueda de persona por ID
           - PUT /personas/{id} → actualización de persona
           - DELETE /personas/{id} → baja de persona
        - Validaciones implementadas:
           - Cálculo automático de edad a partir de la fecha de nacimiento.
           - No se permite fecha de nacimiento futura.
           - Email y DNI deben ser únicos → en caso de duplicados, retorna error HTTP 400.
           - Manejo de errores controlado para evitar que el servidor se caiga (Internal Server Error).
