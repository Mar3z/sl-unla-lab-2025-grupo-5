from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal  #Me aseguro de que exista database.py con SessionLocal
from database import engine
from models import Base

app = FastAPI()

#Endpoint de prueba
@app.get("/")
def inicio():
    return {"mensaje": "Probando si funciona la api"}

#Funcion para obtener la sesion de la base
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Creo tablas
Base.metadata.create_all(bind=engine)
