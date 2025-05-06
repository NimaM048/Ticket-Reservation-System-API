from sqlalchemy.orm import Session
from fastapi import HTTPException
from database.models import DbSeat, DbSeatReservation
from schemas import SeatReservationCreate



def reserve_seat(db: Session, seat_reservation: SeatReservationCreate):

    seat = db.query(DbSeat).filter(DbSeat.id == seat_reservation.seat_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")


    already_reserved = db.query(DbSeatReservation).filter(
        DbSeatReservation.seat_id == seat_reservation.seat_id,
        DbSeatReservation.event_id == seat_reservation.event_id,
        DbSeatReservation.is_paid == True
    ).first()

    if already_reserved:
        return None

    # رزرو جدید ایجاد کنیم
    new_reservation = DbSeatReservation(
        seat_id=seat_reservation.seat_id,
        reservation_id=seat_reservation.reservation_id,
        event_id=seat_reservation.event_id,
        is_paid=seat_reservation.is_paid
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation


def get_reservations_by_event(db: Session, event_id: int):
    return db.query(DbSeatReservation).filter(DbSeatReservation.event_id == event_id).all()


def get_reservations_by_user(db: Session, user_id: int):
    return db.query(DbSeatReservation).join(DbSeatReservation.reservation).filter(
        DbSeatReservation.reservation.has(user_id=user_id)
    ).all()


def cancel_seat_reservation(db: Session, seat_reservation_id: int):
    seat_reservation = db.query(DbSeatReservation).filter(
        DbSeatReservation.id == seat_reservation_id
    ).first()

    if not seat_reservation:
        return None

    db.delete(seat_reservation)
    db.commit()
    return seat_reservation
