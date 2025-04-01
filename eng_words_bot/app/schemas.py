# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    # В реальном приложении здесь будет password: str
    pass

class User(UserBase):
    id: int
    # profile_picture: Optional[str] = None

    class Config:
        orm_mode = True # Позволяет Pydantic работать с объектами SQLAlchemy

# --- Post Schemas ---
class PostBase(BaseModel):
    text_content: Optional[str] = None

class PostCreate(PostBase):
     # image не здесь, он будет UploadFile в эндпоинте
     pass

class Post(PostBase):
    id: int
    image_path: Optional[str] = None
    timestamp: datetime.datetime
    owner_id: int
    owner: User # Включаем информацию о владельце поста

    class Config:
        orm_mode = True