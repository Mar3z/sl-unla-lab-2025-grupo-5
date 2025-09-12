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
    
    # Verificar si ya existe email o DNI
    if db.query(Persona).filter(Persona.email == persona.email).first():
        raise HTTPException(status_code=400, detail="E-mail ya registrado")
    if db.query(Persona).filter(Persona.dni == persona.dni).first():
        raise HTTPException(status_code=400, detail="DNI ya registrado")

    db_persona = Persona(
        nombre=persona.nombre,
        email=persona.email,
        dni=persona.dni,
        telefono=persona.telefono,
        fecha_nacimiento=persona.fecha_nacimiento,
        habilitado=persona.habilitado
    )

    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona

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
    for key, value in datos.dict().items():
        setattr(persona, key, value)
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
