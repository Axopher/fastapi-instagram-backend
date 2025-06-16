from pydantic import BaseModel
from typing import Optional
from ..auth.schemas import UserBase


class Profile(UserBase):
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0

    class Config:
        orm_mode = True
        from_attributes = True


class UserSchema(BaseModel):
    profile_pic: Optional[str] = None
    username: str
    name: Optional[str] = None

    class Config:
        orm_mode = True  # Hey, I might receive SQLAlchemy model instances — please extract fields using getattr() is what orm_mode does.


class FollowingList(BaseModel):
    following: Optional[list[UserSchema]] = []


class FollowersList(BaseModel):
    followers: Optional[list[UserSchema]] = []
