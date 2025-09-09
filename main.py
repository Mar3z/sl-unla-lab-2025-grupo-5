from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal,engine,Base  #Me aseguro de que exista database.py con SessionLocal
from models import Persona
from schemas import PersonaCreate,Persona as PersonaSchema
from datetime import date
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
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona

#Obtener personas / GET

@app.get("/personas", response_model=list[PersonaSchema])
def listar_personas(db: Session = Depends(get_db)):
    return db.query(Persona).all()
