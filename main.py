
#Importamos FastAPI y herramientas:
# FastAPI: el framework,Depends: para inyectar dependencias (ej. sesiones de DB), HTTPException: para lanzar errores personalizados en la API
from fastapi import FastAPI, Depends,HTTPException
#importamos sessiones
from sqlalchemy.orm import Session
 #Me aseguro de que exista database.py con SessionLocal, e importo lo necesario
from database import SessionLocal,engine,Base 
#Importamos el modelo Persona (tabla en DB)
from models import Persona 
#Importamos esquemas Pydantic (para validaciones y respuestas)
from schemas import PersonaCreate,Persona as PersonaSchema 
#Importamos date para trabajar con fechas
from datetime import date 
#Importamos excepción de SQLAlchemy para manejar duplicados (unique)
from sqlalchemy.exc import IntegrityError 

from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal,engine,Base  #Me aseguro de que exista database.py con SessionLocal
from models import Persona
from schemas import PersonaCreate,Persona as PersonaSchema
from datetime import date
from sqlalchemy.exc import IntegrityError

#Creo tablas
Base.metadata.create_all(bind=engine)
app = FastAPI()

#Endpoint de prueba
"""@app.get("/")
def inicio():
    return {"mensaje": "Probando si funciona la api"}"""

#Funcion para obtener la sesion de la base
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Funcion para calcular edad
def calcular_edad(fecha_nacimiento: date):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

# ----- ENDPOINTS DE PERSONAS (CRUD) -----

#Crear persona / POST

@app.post("/personas", response_model=PersonaSchema)
def crear_persona(persona: PersonaCreate, db: Session = Depends(get_db)):



    #Validacion:la fecha de nacimiento no puede ser futura
    if persona.fecha_nacimiento > date.today():
        raise HTTPException(
            status_code=400,
            detail="La fecha de nacimiento no puede ser futura"
        )
    

    #Calcular edad automáticamente
    edad = calcular_edad(persona.fecha_nacimiento)
    #Crear instancia de Persona (modelo DB)

    
    edad = calcular_edad(persona.fecha_nacimiento)

    db_persona = Persona(
        nombre=persona.nombre,
        email=persona.email,
        dni=persona.dni,
        telefono=persona.telefono,
        fecha_nacimiento=persona.fecha_nacimiento,
        edad=edad,
        habilitado=True
    )

    #Agregar a la sesión
    db.add(db_persona)
    try:
        #Guardar cambios en la DB
        db.commit()
        #Refrescar el objeto con los datos guardados
        db.refresh(db_persona)
        return db_persona
    except IntegrityError:
        #Si hay error por duplicados, revertimos cambios
        db.rollback()  

    db.add(db_persona)
    try:
        db.commit()
        db.refresh(db_persona)
        return db_persona
    except IntegrityError:
        db.rollback()  # revertir cambios de la sesión

        raise HTTPException(
            status_code=400, 
            detail="Error: DNI o email ya registrado"
        )
#Obtener todas las personas / GET

@app.get("/personas", response_model=list[PersonaSchema])
def listar_personas(db: Session = Depends(get_db)):
    return db.query(Persona).all()

#Obtener persona por ID / GET

@app.get("/personas/{id}", response_model=PersonaSchema)
def obtener_persona(id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

#Actualizar personas por id / PUT

@app.put("/personas/{id}", response_model=PersonaSchema)
def actualizar_persona(id: int, datos: PersonaCreate, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    #Actualizar todos los atributos de Persona con los datos recibidos
    for key, value in datos.dict().items():
        setattr(persona, key, value)
    #Recalcular edad con la nueva fecha de nacimiento

    for key, value in datos.dict().items():
        setattr(persona, key, value)

    persona.edad = calcular_edad(datos.fecha_nacimiento)
    db.commit()
    db.refresh(persona)
    return persona

#Eliminar personas por id/ DELETE

@app.delete("/personas/{id}")
def eliminar_persona(id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    db.delete(persona)
    db.commit()
    return {"mensaje": "Persona eliminada"}
