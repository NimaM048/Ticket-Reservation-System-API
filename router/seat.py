from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import db_seat
from database.db import get_db
from database.models import DbHall, DbSeat
from schemas import SeatCreate, SeatDisplay, BulkSeatTypeUpdate

router = APIRouter(
    prefix="/seat",
    tags=["Seat"]
)


@router.post('/', response_model=SeatDisplay)
def create_seat(seat: SeatCreate, db: Session = Depends(get_db)):
    return db_seat.create_seat(db, seat)


@router.get('/hall/{hall_id}', response_model=list[SeatDisplay])
def get_seats_by_hall(hall_id: int, db: Session = Depends(get_db)):
    seats = db_seat.get_seats_by_hall(db, hall_id)
    if not seats:
        raise HTTPException(status_code=404, detail="No seats found for this hall")
    return seats


@router.get('/{seat_id}', response_model=SeatDisplay)
def get_seat_by_id(seat_id: int, db: Session = Depends(get_db)):
    seat = db_seat.get_seat_by_id(db, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return seat


@router.put('/{seat_id}', response_model=SeatDisplay)
def update_seat(seat_id: int, seat: SeatCreate, db: Session = Depends(get_db)):
    updated_seat = db_seat.update_seat(db, seat_id, seat)
    if not updated_seat:
        raise HTTPException(status_code=404, detail="Seat not found for update")
    return updated_seat


@router.delete('/{seat_id}')
def delete_seat(seat_id: int, db: Session = Depends(get_db)):
    deleted_seat = db_seat.delete_seat(db, seat_id)
    if not deleted_seat:
        raise HTTPException(status_code=404, detail="Seat not found for deletion")
    return {"detail": "Seat deleted successfully"}



@router.put("/bulk-update/")
def bulk_update_seats(
    hall_id: int,
    seat_type: str,
    row_from: int = None,
    row_to: int = None,
    col_from: int = None,
    col_to: int = None,
    db: Session = Depends(get_db)
):
    updated = db_seat.bulk_update_seats(
        db, hall_id, seat_type, row_from, row_to, col_from, col_to
    )
    return {"detail": f"{updated} seats updated to type '{seat_type}'"}




@router.put("/bulk/update-seat-type")
def bulk_update_seat_type(data: BulkSeatTypeUpdate, db: Session = Depends(get_db)):
    seats = db.query(DbSeat).filter(DbSeat.id.in_(data.seat_ids)).all()
    if not seats:
        raise HTTPException(status_code=404, detail="No seats found")

    for seat in seats:
        seat.seat_type = data.new_seat_type

    db.commit()
    return {"detail": f"Updated {len(seats)} seats to '{data.new_seat_type}'"}
