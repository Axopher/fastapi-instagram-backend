from sqlalchemy.orm import Session
from datetime import datetime
import re
from sqlalchemy import desc

from ..auth.service import get_current_user
from .schemas import PostCreate, Post as PostSchema, Hashtag as HashtagScehma
from .models import Post, Hashtag, post_hashtags
from ..auth.models import User
from ..auth.schemas import User as UserSchema
from ..activity.service import create_like_activity


#  create hashing from posts' content
async def create_hashtags_svc(db: Session, post: Post):
    regex = r"#\w+"
    matches = re.findall(regex, post.content)
    for match in matches:
        name = match[1:]

        hashtag = db.query(Hashtag).filter(Hashtag.name == name).first()
        if not hashtag:
            hashtag = Hashtag(name=name)
            db.add(hashtag)
        post.hashtags.append(hashtag)


# create post
async def create_post_svc(db: Session, post: PostCreate, user_id: int):
    db_post = Post(
        content=post.content,
        image=post.image,
        location=post.location,
        author_id=user_id,
    )

    await create_hashtags_svc(db, db_post)

    db.add(db_post)
    db.commit()
    return db_post


# get user's posts
async def get_users_posts_svc(db: Session, user_id: int) -> list[PostSchema]:
    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id)
        .order_by(desc(Post.created_at))
        .all()
    )
    return posts


# get posts from a hashtag
async def get_posts_from_hashtag_svc(db: Session, hashtag_name: str):
    hashtag = db.query(Hashtag).filter_by(name=hashtag_name).first()
    if not hashtag:
        return None
    return hashtag.posts


# get random posts for feed
# return latest posts of all users
async def get_random_posts_svc(
    db: Session, page: int = 1, limit: int = 10, hashtag: str = None
):
    total_posts = db.query(Post).count()
    offset = (page - 1) * limit  # 0-9 posts 10-19 posts and so on logic.
    if offset >= total_posts:
        return []
    posts = db.query(Post, User.username).join(User).order_by(desc(Post.created_at))

    if hashtag:
        posts = posts.join(post_hashtags).join(Hashtag).filter(Hashtag.name == hashtag)

    posts = posts.offset(offset).limit(limit).all()

    result = []
    for post, username in posts:
        post_dict = post.__dict__
        post_dict["username"] = username
        result.append(post_dict)

    return result


# get post by post id
async def get_post_from_post_id_svc(db: Session, post_id: int) -> PostSchema:
    return db.query(Post).filter(Post.id == post_id).first()


# delete post svc
async def delete_post_from_post_id_svc(db: Session, post_id: int) -> PostSchema:
    post = await get_post_from_post_id_svc(db, post_id)
    db.delete(post)
    db.commit()


# like a post
async def like_post_svc(db: Session, post_id: int, token: str):
    user = await get_current_user(db, token)
    if not user:
        return False, "Not Authorized"

    post = await get_post_from_post_id_svc(db, post_id)
    if not post:
        return False, "Invalid post_id"

    if user in post.liked_by_users:
        return False, "already liked."

    post.liked_by_users.append(user)
    post.likes_count = len(post.liked_by_users)

    # TO DO activity of like
    await create_like_activity(db, post.author, user, post)

    db.commit()
    return True, "done"


# unlike post
async def unlike_post_svc(db: Session, post_id: int, token: str):
    user = await get_current_user(db, token)
    if not user:
        return False, "Not authorized."

    post = await get_post_from_post_id_svc(db, post_id)
    if not post:
        return False, "Invalid post_id"

    if user not in post.liked_by_users:
        return False, "already not liked."

    post.liked_by_users.remove(user)
    post.likes_count = len(post.liked_by_users)

    db.commit()

    return True, "done"


# users who liked post
async def liked_users_post_svc(db: Session, post_id: int) -> list[UserSchema]:
    post = await get_post_from_post_id_svc(db, post_id)
    if not post:
        return False, "No such posts."

    liked_users = post.liked_by_users
    # # in case we don't have orm mode in UserSchema
    # return [UserSchema.from_orm(user) for user in liked_users]

    # since UserSchema has orm_mode so we can directly use this
    return liked_users
