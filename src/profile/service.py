from sqlalchemy.orm import Session
from ..auth.models import User, Follow
from ..activity.models import Activity
from .schemas import FollowersList, FollowingList, Profile
from ..auth.service import get_current_user, existing_user


# follow
async def follow_svc(db: Session, follower: str, following: str):
    db_follower = await existing_user(db, follower, "")
    db_following = await existing_user(db, following, "")

    if not db_follower or not db_following or db_follower.id == db_following.id:
        return False, "could not follow."

    # one way to do it would be
    # -------------------------------------------------------------------------------
    ## Check via the relationship
    # for rel in db_follower.following:
    #     if rel.following_id == db_following.id:
    #         return False  # already following

    ## Append via relationship
    # db_follower.following.append(Follow(following=db_following))

    ### Explanation:-
    ## Here, SQLAlchemy internally resolves it like:
    # Follow(
    #     follower=db_follower,  # inferred from relationship
    #     following=db_following,  # explicitly passed
    # )
    # # which in turn sets
    # Follow(follower_id=db_follower.id, following_id=db_following.id)
    # ----------------------------------------------------------------------------------

    db_follow = (
        db.query(Follow)
        .filter_by(follower_id=db_follower.id, following_id=db_following.id)
        .first()
    )
    if db_follow:
        return False, "Already Followed."

    db_follow = Follow(follower_id=db_follower.id, following_id=db_following.id)
    db.add(db_follow)

    # db_follower.following_count = (
    #     db.query(Follow).filter_by(follower_id=db_follower.id).count()
    # )
    # db_following.followers_count = (
    #     db.query(Follow).filter_by(following_id=db_following.id).count()
    # )

    # Think of flush() like hitting "Save Draft" — your changes are written, but not yet published.
    db.flush()  # After flushing, the database state is updated, and you can run queries that rely on the new state
    db.refresh(
        db_follower
    )  # Re-reads the given object (obj) from the database and updates the in-memory Python object with fresh data.
    db.refresh(db_following)
    db_follower.following_count = len(db_follower.following)
    db_following.followers_count = len(db_following.followers)

    follow_activity = Activity(
        username=following,
        followed_username=db_follower.username,
        followed_user_pic=db_follower.profile_pic,
    )

    db.add(follow_activity)

    db.commit()
    return True, ""


async def unfollow_svc(db: Session, follower: str, following: str):
    db_follower = await existing_user(db, follower, "")
    db_following = await existing_user(db, following, "")

    if not db_follower or not db_following or db_follower.id == db_following.id:
        return False, "could not unfollow."

    db_follow = (
        db.query(Follow)
        .filter(
            Follow.follower_id == db_follower.id, Follow.following_id == db_following.id
        )
        .first()
    )
    if not db_follow:
        return False, "already unfollowed."

    db.delete(db_follow)

    # db.flush()
    # db.refresh(db_follower)
    # db.refresh(db_following)
    # db_follower.following_count = len(db_follower.following)
    # db_following.followers_count = len(db_following.followers)

    # for better accuracy but Slightly slower because it makes an extra query to the DB.
    db.flush()  # After flushing, the database state is updated, and you can run queries that rely on the new state
    db_follower.following_count = (
        db.query(Follow).filter(Follow.follower_id == db_follower.id).count()
    )
    db_following.followers_count = (
        db.query(Follow).filter(Follow.following_id == db_following.id).count()
    )

    db.commit()
    return True, ""


# get followers
async def get_followers_svc(
    db: Session, user_id: int, skip: int = 1, limit: int = 10
) -> FollowersList:
    skip = (skip - 1) * 10
    db_followers = (
        db.query(User)
        .join(Follow, Follow.follower_id == User.id)
        .filter(Follow.following_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return db_followers

    # followers = [
    #     {
    #         "profile_pic": follower.profile_pic,
    #         "name": follower.name,
    #         "username": follower.username,
    #     }
    #     for follower in follower_users
    # ]

    # return FollowersList(followers)


# get followings
async def get_following_svc(
    db: Session, user_id: int, skip: int = 0, limit: int = 0
) -> FollowersList:
    db_followings = (
        db.query(User)
        .join(Follow, Follow.following_id == User.id)
        .filter(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return db_followings


async def check_follow_svc(db: Session, follower: str, followed: str):
    db_follower = await existing_user(db, follower, "")
    db_following = await existing_user(db, followed, "")

    if not db_follower or not db_following or db_follower.id == db_following.id:
        return False

    db_following = (
        db.query(Follow)
        .filter_by(follower_id=db_follower.id, following_id=db_following.id)
        .first()
    )
    if not db_following:
        return False

    return True
