from fastapi import HTTPException
from sqlalchemy.orm import Session

from database.models import DbSeat, DbHall
from schemas import SeatCreate



def create_seat(db: Session, seat: SeatCreate):
    hall = db.query(DbHall).filter(DbHall.id == seat.hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="Hall not found")

    if seat.row < 1 or seat.row > hall.total_rows:
        raise HTTPException(status_code=400, detail="Invalid row number")

    if seat.number < 1 or seat.number > hall.total_columns:
        raise HTTPException(status_code=400, detail="Invalid seat number")

    new_seat = DbSeat(
        hall_id=seat.hall_id,
        row=seat.row,
        number=seat.number,
        seat_type=seat.seat_type,
        is_reserved=seat.is_reserved
    )
    db.add(new_seat)
    db.commit()
    db.refresh(new_seat)
    return new_seat


def get_seats_by_hall(db: Session, hall_id: int):
    return db.query(DbSeat).filter(DbSeat.hall_id == hall_id).all()


def get_seat_by_id(db: Session, seat_id: int):
    return db.query(DbSeat).filter(DbSeat.id == seat_id).first()


def update_seat(db: Session, seat_id: int, seat_data: SeatCreate):
    seat = db.query(DbSeat).filter(DbSeat.id == seat_id).first()
    if seat:
        seat.hall_id = seat_data.hall_id
        seat.row = seat_data.row
        seat.number = seat_data.number
        seat.seat_type = seat_data.seat_type
        seat.is_reserved = seat_data.is_reserved
        db.commit()
        db.refresh(seat)
    return seat


# حذف صندلی
def delete_seat(db: Session, seat_id: int):
    seat = db.query(DbSeat).filter(DbSeat.id == seat_id).first()
    if seat:
        db.delete(seat)
        db.commit()
    return seat


def bulk_update_seats(db: Session, hall_id: int, seat_type: str, row_from=None, row_to=None, col_from=None, col_to=None):
    query = db.query(DbSeat).filter(DbSeat.hall_id == hall_id)

    if row_from is not None and row_to is not None:
        query = query.filter(DbSeat.row.between(row_from, row_to))

    if col_from is not None and col_to is not None:
        query = query.filter(DbSeat.number.between(col_from, col_to))

    updated_count = 0
    for seat in query.all():
        seat.seat_type = seat_type
        updated_count += 1

    db.commit()
    return updated_count

