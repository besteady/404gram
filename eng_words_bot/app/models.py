# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Для установки времени по умолчанию
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # В реальном приложении здесь будет хэш пароля, дата регистрации и т.д.
    # profile_picture = Column(String, nullable=True) # Путь к аватарке

    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text_content = Column(Text, nullable=True)
    image_path = Column(String, nullable=True) # Путь к сохраненному изображению
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="posts")