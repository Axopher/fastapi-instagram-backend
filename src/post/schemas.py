from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Hashtag(BaseModel):
    id: int
    name: str


class PostCreate(BaseModel):
    image: str
    content: Optional[str] = None
    location: Optional[str] = None


class Post(PostCreate):
    id: int
    author_id: int
    likes_count: int
    created_at: datetime

    class Config:
        orm_mode = True
