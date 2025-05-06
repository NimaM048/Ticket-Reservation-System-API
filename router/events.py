from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import math
from database import db_event
from database.db import get_db
from database.db_event import calculate_seat_layout
from database.models import DbHall, DbEvent, DbSeat
from schemas import EventDisplay, EventBase


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)



@router.post("/", response_model=EventDisplay, status_code=status.HTTP_201_CREATED)
def create_event(event: EventBase, db: Session = Depends(get_db)):

    hall = None
    if event.hall_id and event.hall_id != 0:
        hall = db.query(DbHall).filter(DbHall.id == event.hall_id).first()
        if not hall:
            raise HTTPException(status_code=404, detail="Hall not found")
    else:


        total_seats = event.total_tickets
        columns = math.isqrt(total_seats)
        if columns * columns < total_seats:
            columns += 1
        rows = math.ceil(total_seats / columns)

        hall = DbHall(
            name=f"Auto Hall for {event.title}",
            total_rows=rows,
            total_columns=columns,
            total_seats=rows * columns
        )
        db.add(hall)
        db.commit()
        db.refresh(hall)


        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                if (row - 1) * columns + column <= total_seats:
                    seat = DbSeat(
                        hall_id=hall.id,
                        row=str(row),
                        number=column,
                        seat_type='NORMAL'
                    )
                    db.add(seat)
        db.commit()

    db_event = DbEvent(
        title=event.title,
        description=event.description,
        date=event.date,
        location=event.location,
        total_tickets=event.total_tickets,
        available_tickets=event.available_tickets if event.available_tickets is not None else event.total_tickets,
        hall_id=hall.id
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.get("/{event_id}", response_model=EventDisplay)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db_event.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/", response_model=list[EventDisplay])
def get_all_events(db: Session = Depends(get_db)):
    events = db.query(DbEvent).all()
    return events


@router.put("/{event_id}", response_model=EventDisplay)
def update_event(event_id: int, event: EventBase, db: Session = Depends(get_db)):
    updated_event = db_event.update_event(db, event_id, event)
    if not updated_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return updated_event


@router.delete("/{event_id}", response_model=EventDisplay)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    deleted_event = db_event.delete_event(db, event_id)
    if not deleted_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return deleted_event
