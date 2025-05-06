from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import Session
from auth.auth import verify_access_token
from auth.authentication import oauth2_scheme
from schemas import UserBase, UserDisplay
from database import dbuser
from database.db import get_db
from database.models import DbUsers
from auth.dependencies import get_admin_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/", response_model=List[UserDisplay])
def read_all_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), admin_user: DbUsers = Depends(get_admin_user)):
    return dbuser.read_all_users(db)


@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), admin_user: DbUsers = Depends(get_admin_user)):

    return dbuser.delete_user(id, db)


@router.get("/{id}", response_model=UserDisplay)
def read_user(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return dbuser.read_user(id, db)

@router.put("/{id}", response_model=UserDisplay)
def update_user(id: int, user: UserBase = Body(...), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    db_user = dbuser.update_user(id, user, db)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
