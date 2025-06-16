from sqlalchemy.orm import Session
from .models import Activity
from ..auth.schemas import User
from ..post.schemas import Post


# get activity of a user by username
async def get_activities_by_username(
    db: Session, username: str, page: int = 1, limit: int = 10
) -> list[Activity]:
    offset = (page - 1) * 10
    return (
        db.query(Activity)
        .filter(Activity.username == username)
        .order_by(Activity.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


async def create_like_activity(
    db: Session,
    recipient_user: User,  # user receiving the activity (post author)
    actor_user: User,  # user who liked the post
    post: Post,  # the post that was liked
):
    like_activity = Activity(
        username=recipient_user.username,
        liked_post_id=post.id,
        username_like=actor_user.username,
        liked_post_image=post.image,
        followed_username=actor_user.username,
        followed_user_pic=actor_user.profile_pic,
    )
    db.add(like_activity)
