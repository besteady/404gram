# app/crud.py
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func # Для random()
import datetime
from . import models, schemas
from .pipelines import images_pipeline, text_pipeline
import shutil
import os
from fastapi import UploadFile

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    # В реальном приложении здесь будет хэширование пароля
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Post CRUD ---

# Папка для сохранения изображений
UPLOAD_DIR = "static/images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def create_post(db: Session, post_data: schemas.PostCreate, user_id: int, image: Optional[UploadFile] = None):
    image_path_db = None
    if image:
        # Проверяем тип файла (базовая проверка)
        if image.content_type not in ["image/jpeg", "image/png", "image/gif"]:
             raise ValueError("Invalid image type. Only JPG, PNG, GIF allowed.")

        # Генерируем безопасное имя файла (можно использовать uuid)
        # Простое имя для примера: user_<id>_post_<timestamp>.<ext>
        file_extension = os.path.splitext(image.filename)[1]
        # Безопаснее генерировать уникальное имя, чтобы избежать коллизий
        # import uuid; unique_filename = f"{uuid.uuid4()}{file_extension}"
        # Для простоты пока используем имя файла (небезопасно!)
        image_filename = f"post_{user_id}_{datetime.datetime.now().timestamp()}{file_extension}".replace(" ", "_")
        image_path_server = os.path.join(UPLOAD_DIR, image_filename)
        image_path_db = f"/static/images/{image_filename}" # Путь для доступа через веб

        # Сохраняем файл
        try:
            with open(image_path_server, "wb") as buffer:
                imfile = image.file
                for p in images_pipeline:
                    imfile = p(imfile)
                shutil.copyfileobj(imfile, buffer)
        finally:
            image.file.close() # Важно закрыть файл

    text_co = post_data.text_content
    for p in text_pipeline:
        text_co = p(text_co)

    # Создаем запись в БД
    db_post = models.Post(
        text_content=text_co,
        image_path=image_path_db,
        owner_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts_random_feed(db: Session, limit: int = 10):
    # Получаем случайные посты. Для SQLite используем RANDOM()
    # Для PostgreSQL: func.random()
    # Для MySQL: func.rand()
    return db.query(models.Post).order_by(func.random()).limit(limit).all()

def get_posts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Post).filter(models.Post.owner_id == user_id).order_by(models.Post.timestamp.desc()).offset(skip).limit(limit).all()