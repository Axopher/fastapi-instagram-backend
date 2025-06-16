# db models

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from .enums import Gender
from ..post.models import post_likes
from sqlalchemy import text


# this is another way to create assoication table as we have done for post_hashtags and post_likes
class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    follower = relationship(
        "User", foreign_keys=[follower_id], back_populates="followers"
    )
    following = relationship(
        "User", foreign_keys=[following_id], back_populates="following"
    )


# It basically means:
# follow = Follow(follower=user1, following=user2)
# print(follow.follower.name)   # user1
# print(follow.following.name)  # user2


class User(Base):
    __tablename__ = "users"

    # basic details
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())

    # profile
    dob = Column(Date)
    gender = Column(Enum(Gender))
    profile_pic = Column(String)
    bio = Column(String)
    location = Column(String)

    posts = relationship("post.models.Post", back_populates="author")

    liked_posts = relationship(
        "post.models.Post", secondary=post_likes, back_populates="liked_by_users"
    )

    # Users who follow me
    followers = relationship(
        Follow,
        foreign_keys=[Follow.following_id],
        back_populates="following",
        cascade="all, delete-orphan",
    )
    # Users I am following
    following = relationship(
        Follow,
        foreign_keys=[Follow.follower_id],
        back_populates="follower",
        cascade="all, delete-orphan",
    )

    following_count = Column(Integer, default=0, server_default=text("0"))
    followers_count = Column(Integer, default=0, server_default=text("0"))
