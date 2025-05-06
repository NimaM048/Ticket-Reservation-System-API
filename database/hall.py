from sqlalchemy.orm import Session
from fastapi import HTTPException

from database.models import DbHall, DbSeat
from schemas import HallCreate

# ساخت خودکار صندلی‌ها بعد از ساخت سالن
def create_seats_for_hall(db: Session, hall_id: int, total_rows: int, total_columns: int):
    seats = []
    for row in range(1, total_rows + 1):
        for number in range(1, total_columns + 1):
            seat = DbSeat(
                hall_id=hall_id,
                row=row,
                number=number,
                seat_type="normal"
            )
            db.add(seat)
            seats.append(seat)
    db.commit()
    return seats


def create_hall(db: Session, request: HallCreate):
    new_hall = DbHall(
        name=request.name,
        total_rows=request.total_rows,
        total_columns=request.total_columns,
        total_seats=request.total_rows * request.total_columns
    )
    db.add(new_hall)
    db.commit()
    db.refresh(new_hall)


    try:
        create_seats_for_hall(db, new_hall.id, new_hall.total_rows, new_hall.total_columns)
    except Exception as e:
        db.delete(new_hall)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error while creating seats: {e}")

    return new_hall


def get_all_halls(db: Session):
    return db.query(DbHall).all()
