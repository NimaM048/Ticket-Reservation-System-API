from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.authentication import oauth2_scheme
from auth.auth import verify_access_token
from auth.dependencies import get_admin_user
from database import db_reservation
from database.db import get_db
from database.models import DbUsers, DbEvent, DbReservation
from schemas import ReservationDisplay, ReservationBase


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)




@router.get("/", response_model=list[ReservationDisplay])
def get_user_reservations(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = db.query(DbUsers).filter(DbUsers.username == username).first().id
    return db_reservation.get_reservations_by_user(db, user_id)





@router.post("/{reservation_id}/cancel", response_model=ReservationDisplay)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(DbUsers).filter(DbUsers.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reservation = db.query(DbReservation).filter(DbReservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    if reservation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only cancel your own reservations")

    if reservation.is_canceled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation already canceled")

    if reservation.is_paid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paid reservations cannot be canceled")

    event = db.query(DbEvent).filter(DbEvent.id == reservation.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    reservation.is_canceled = True
    event.available_tickets += reservation.quantity

    db.commit()
    db.refresh(reservation)

    return reservation

