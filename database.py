<<<<<<< HEAD
#Importamos las funciones necesarias de SQLAlchemy:
from sqlalchemy import create_engine #create_engine: se usa para crear la conexion al motor de base de datos
from sqlalchemy.orm import sessionmaker, declarative_base #sessionmaker: sirve para crear sesiones con la base de datos (interaccion)
                                                          #declarative_base: clase base para definir nuestros modelos/tablas

#Base de datos SQLite, URL de conexion a la base de datos
DATABASE_URL = "sqlite:///./turnos.db"

#Creamos el engine con la URL de la base de datos
#connect_args={"check_same_thread": False} es necesario solo en SQLite,para permitir que multiples hilos accedan a la misma conexión
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

#Creamos la fabrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Creamos la clase base para todos los modelos (tablas),todas las clases de nuestras tablas heredaran de Base.
=======
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#Base de datos SQLite
DATABASE_URL = "sqlite:///./turnos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

>>>>>>> origin/main
Base = declarative_base()
