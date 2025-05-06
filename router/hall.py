from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import hall
from database.db import get_db
from typing import List

from database.models import DbSeat
from schemas import HallCreate, HallDisplay, SeatDisplay

router = APIRouter(
    prefix="/hall",
    tags=["Hall Management"]
)

@router.post("/", response_model=HallDisplay)
def create_hall(request: HallCreate, db: Session = Depends(get_db)):
    return hall.create_hall(db, request)

@router.get("/", response_model=List[HallDisplay])
def get_all_halls(db: Session = Depends(get_db)):
    return hall.get_all_halls(db)


@router.get("/{hall_id}/seats", response_model=list[SeatDisplay])
def get_seats_by_hall(hall_id: int, db: Session = Depends(get_db)):
    seats = db.query(DbSeat).filter(DbSeat.hall_id == hall_id).all()
    if not seats:
        raise HTTPException(status_code=404, detail="Seats not found for this hall")
    return seats
