from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.auth import verify_access_token
from auth.authentication import oauth2_scheme
from database import seat_reservation_db
from database.db import get_db
from database.models import DbSeat, DbEvent, DbUsers, DbSeatReservation, DbReservation
from schemas import SeatReservationDisplay, SeatReservationCreate

router = APIRouter(
    prefix="/seat-reservation",
    tags=["Seat Reservation"]
)


@router.post('/seat-reservation/', response_model=List[SeatReservationDisplay])
def reserve_seat(
        seat_reservation: SeatReservationCreate,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    # Verify user authentication
    username = verify_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user from database
    user = db.query(DbUsers).filter(DbUsers.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if event exists
    event = db.query(DbEvent).filter(DbEvent.id == seat_reservation.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check ticket availability
    if event.available_tickets < len(seat_reservation.seat_ids):
        raise HTTPException(status_code=400, detail="Not enough tickets available")

    # Get or create reservation record
    reservation = db.query(DbReservation).filter(
        DbReservation.user_id == user.id,
        DbReservation.event_id == event.id,
        DbReservation.is_canceled == False
    ).first()

    if not reservation:
        reservation = DbReservation(
            user_id=user.id,
            event_id=event.id,
            quantity=0
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

    reserved_seats = []

    for seat_id in seat_reservation.seat_ids:
        # Check if seat is already reserved
        existing_reservation = db.query(DbSeatReservation).filter(
            DbSeatReservation.seat_id == seat_id,
            DbSeatReservation.event_id == seat_reservation.event_id,
            DbSeatReservation.is_canceled == False,
            (
                    (DbSeatReservation.is_paid == True) |
                    (DbSeatReservation.expires_at > datetime.now(timezone.utc))
            )
        ).first()

        if existing_reservation:
            raise HTTPException(
                status_code=400,
                detail=f"Seat {seat_id} is already reserved"
            )


        new_seat_reservation = DbSeatReservation(
            seat_id=seat_id,
            reservation_id=reservation.id,
            event_id=event.id,
            is_paid=seat_reservation.is_paid,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1)
        )
        db.add(new_seat_reservation)


        seat = db.query(DbSeat).filter(DbSeat.id == seat_id).first()
        if seat:
            seat.is_reserved = True

        reserved_seats.append(new_seat_reservation)


    reservation.quantity = len([
        sr for sr in reservation.seat_reservations if not sr.is_canceled
    ])


    event.available_tickets -= len(reserved_seats)

    db.commit()

    return reserved_seats



@router.get('/event/{event_id}', response_model=list[SeatReservationDisplay])
def get_reservations_by_event(event_id: int, db: Session = Depends(get_db)):
    reservations = seat_reservation_db.get_reservations_by_event(db, event_id)
    return reservations


@router.get('/user/{user_id}', response_model=list[SeatReservationDisplay])
def get_reservations_by_user(user_id: int, db: Session = Depends(get_db)):
    reservations = seat_reservation_db.get_reservations_by_user(db, user_id)
    return reservations


@router.post('/seat-reservation/{reservation_id}/cancel', response_model=SeatReservationDisplay)
def cancel_seat_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    username = verify_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(DbUsers).filter(DbUsers.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    seat_reservation = db.query(DbSeatReservation).filter(
        DbSeatReservation.id == reservation_id
    ).first()

    if not seat_reservation:
        raise HTTPException(status_code=404, detail="Seat reservation not found")

    if seat_reservation.reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this reservation")

    if seat_reservation.is_canceled:
        raise HTTPException(status_code=400, detail="Reservation already canceled")

    if seat_reservation.is_paid:
        raise HTTPException(status_code=400, detail="Paid reservations cannot be canceled")

    seat_reservation.is_canceled = True

    seat = seat_reservation.seat
    seat.is_reserved = False

    reservation = seat_reservation.reservation
    reservation.quantity = len([
        sr for sr in reservation.seat_reservations
        if not sr.is_canceled
    ])

    event = seat_reservation.event
    event.available_tickets += 1

    db.commit()
    db.refresh(seat_reservation)

    return seat_reservation



@router.put('/seat-reservation/update/', response_model=List[SeatReservationDisplay])
def update_seat_reservation(
    seat_reservation: SeatReservationCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    username = verify_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(DbUsers).filter(DbUsers.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    event = db.query(DbEvent).filter(DbEvent.id == seat_reservation.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    reservation = db.query(DbReservation).filter(
        DbReservation.user_id == user.id,
        DbReservation.event_id == event.id,
        DbReservation.is_canceled == False
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")


    paid_seat = db.query(DbSeatReservation).filter(
        DbSeatReservation.reservation_id == reservation.id,
        DbSeatReservation.is_paid == True,
        DbSeatReservation.is_canceled == False
    ).first()
    if paid_seat:
        raise HTTPException(status_code=400, detail="Cannot update a paid reservation")

    now = datetime.now(timezone.utc)


    for seat_id in seat_reservation.seat_ids:
        existing = db.query(DbSeatReservation).filter(
            DbSeatReservation.seat_id == seat_id,
            DbSeatReservation.event_id == event.id,
            DbSeatReservation.is_canceled == False,
            (
                (DbSeatReservation.is_paid == True) |
                (DbSeatReservation.expires_at > now)
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Seat {seat_id} is already reserved"
            )


    old_reservations = db.query(DbSeatReservation).filter(
        DbSeatReservation.reservation_id == reservation.id,
        DbSeatReservation.is_paid == False,
        DbSeatReservation.is_canceled == False
    ).all()

    for r in old_reservations:
        r.is_canceled = True
        seat = db.query(DbSeat).filter(DbSeat.id == r.seat_id).first()
        if seat:
            seat.is_reserved = False
        event.available_tickets += 1


    new_reservations = []
    for seat_id in seat_reservation.seat_ids:
        new_res = DbSeatReservation(
            seat_id=seat_id,
            reservation_id=reservation.id,
            event_id=event.id,
            is_paid=False,
            expires_at=now + timedelta(minutes=1),
            reserved_at=now
        )
        db.add(new_res)

        seat = db.query(DbSeat).filter(DbSeat.id == seat_id).first()
        if seat:
            seat.is_reserved = True

        new_reservations.append(new_res)

    reservation.quantity = len(new_reservations)
    event.available_tickets -= len(new_reservations)

    db.commit()
    return new_reservations



