# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# DATABASE_URL = "sqlite:///./404gram.db"
# Опционально: использовать PostgreSQL или MySQL
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
# DATABASE_URL = "mysql+mysqlclient://user:password@mysqlserver/db"

# Убедимся, что папка для БД существует (если она не в корне)
# db_dir = os.path.dirname(DATABASE_URL.replace("sqlite:///", ""))
# if db_dir and not os.path.exists(db_dir):
#     os.makedirs(db_dir)

DATABASE_URL = "sqlite:///./404gram.db" # Файл БД будет в корне проекта

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} # Необходимо для SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Функция для создания таблиц (вызывать один раз при старте)
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии БД в эндпоинтах FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()