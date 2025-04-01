from pydantic import BaseModel
from typing import Optional, List
import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    text_content: Optional[str] = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    image_path: Optional[str] = None
    timestamp: datetime.datetime
    owner_id: int
    owner: User

    class Config:
        orm_mode = True
