# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.models import DbUsers, DbReservation
from database.db import get_db
from auth.dependencies import get_admin_user
from schemas import UserDisplay, ReservationDisplay

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users", response_model=list[UserDisplay])
def get_all_users(db: Session = Depends(get_db), admin_user: DbUsers = Depends(get_admin_user)):
    users = db.query(DbUsers).all()
    return users


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), admin_user: DbUsers = Depends(get_admin_user)):
    user = db.query(DbUsers).filter(DbUsers.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return


@router.get("/reservations", response_model=list[ReservationDisplay])
def get_all_reservations(db: Session = Depends(get_db), admin_user: DbUsers = Depends(get_admin_user)):
    reservations = db.query(DbReservation).all()
    return reservations


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationDisplay)
def admin_cancel_reservation(reservation_id: int, db: Session = Depends(get_db), admin_user: DbUsers = Depends(get_admin_user)):
    reservation = db.query(DbReservation).filter(DbReservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    if reservation.is_canceled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation already canceled")

    reservation.is_canceled = True
    db.commit()
    db.refresh(reservation)
    return reservation
