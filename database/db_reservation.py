from sqlalchemy.orm import Session
from database.models import DbReservation, DbEvent
from fastapi import HTTPException, status
from schemas import ReservationBase




def get_reservations_by_user(db: Session, user_id: int):
    return db.query(DbReservation).filter(DbReservation.user_id == user_id).all()
