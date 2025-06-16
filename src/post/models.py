from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

post_hashtags = Table(
    "post_hashtags",
    Base.metadata,
    Column("posts_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("hashtags_id", Integer, ForeignKey("hashtags.id"), primary_key=True),
)

post_likes = Table(
    "post_likes",
    Base.metadata,
    Column("users_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("posts_id", Integer, ForeignKey("posts.id"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"

    # basic details
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    image = Column(String, nullable=True)  # url to the image
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    likes_count = Column(Integer, default=0)

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("auth.models.User", back_populates="posts")

    hashtags = relationship("Hashtag", secondary=post_hashtags, back_populates="posts")

    liked_by_users = relationship(
        "auth.models.User", secondary=post_likes, back_populates="liked_posts"
    )


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    posts = relationship("Post", secondary=post_hashtags, back_populates="hashtags")
