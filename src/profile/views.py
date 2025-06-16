from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .schemas import Profile, FollowersList, FollowingList
from .service import (
    get_followers_svc,
    get_following_svc,
    follow_svc,
    unfollow_svc,
    check_follow_svc,
)
from ..auth.service import existing_user, get_current_user


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/user/{username}", response_model=Profile)
async def profile(username: str, db: Session = Depends(get_db)):
    db_user = await existing_user(db, username, "")
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Username."
        )
    profile = Profile.from_orm(db_user)
    return profile


@router.post("/follow/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def follow_profile(token: str, username: str, db: Session = Depends(get_db)):
    db_user = await get_current_user(db, token)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    res, detail = await follow_svc(db, db_user.username, username)
    if not res:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


@router.post("/unfollow/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_profile(token: str, username: str, db: Session = Depends(get_db)):
    db_user = await get_current_user(db, token)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    res, detail = await unfollow_svc(db, db_user.username, username)
    if not res:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


@router.get(
    "/followers", status_code=status.HTTP_200_OK, response_model=list[FollowersList]
)
async def get_followers(
    token: str, skip: int = 1, limit: int = 10, db: Session = Depends(get_db)
):
    current_user = await get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token."
        )
    return await get_followers_svc(db, current_user.id, skip, limit)


@router.get(
    "/following", status_code=status.HTTP_200_OK, response_model=list[FollowingList]
)
async def get_following(
    token: str, skip: int = 1, limit: int = 10, db: Session = Depends(get_db)
):
    current_user = await get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token."
        )
    return await get_following_svc(db, current_user.id, skip, limit)
