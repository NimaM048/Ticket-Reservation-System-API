from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import UserBase
from database.models import DbUsers
from database.hash import Hash




def read_all_users(db: Session):
    try:
        return db.query(DbUsers).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def read_user(id: int, db: Session):
    try:
        user = db.query(DbUsers).filter(DbUsers.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def delete_user(id: int, db: Session):
    try:
        user = read_user(id, db)
        db.delete(user)
        db.commit()
        return {"detail": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def update_user(id: int, request: UserBase, db: Session):
    try:
        user = db.query(DbUsers).filter(DbUsers.id == id).first()
        if not user:
            return None

        existing_user = db.query(DbUsers).filter(
            ((DbUsers.username == request.username) | (DbUsers.email == request.email)) & (DbUsers.id != id)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already in use")

        user.username = request.username
        user.email = request.email
        user.password = Hash.bcrypt(request.password)

        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
