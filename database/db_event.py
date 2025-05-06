import math
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import DbEvent, DbHall
from schemas import EventBase




def get_all_events(db: Session):
    return db.query(DbEvent).all()

def get_event(db: Session, event_id: int):
    return db.query(DbEvent).filter(DbEvent.id == event_id).first()





def update_event(db: Session, event_id: int, request: EventBase):
    db_event = db.query(DbEvent).filter(DbEvent.id == event_id).first()
    if not db_event:
        return None

    db_event.title = request.title
    db_event.description = request.description
    db_event.date = request.date
    db_event.location = request.location
    db_event.total_tickets = request.total_tickets
    db_event.available_tickets = request.total_tickets

    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int):
    db_event = db.query(DbEvent).filter(DbEvent.id == event_id).first()
    if not db_event:
        return None
    db.delete(db_event)
    db.commit()
    return db_event


def get_filtered_events(
        db: Session,
        title: str = None,
        location: str = None,
        start_date: datetime = None,
        end_date: datetime = None
):
    query = db.query(DbEvent)

    if title:
        query = query.filter(DbEvent.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(DbEvent.location.ilike(f"%{location}%"))
    if start_date:
        query = query.filter(DbEvent.date >= start_date)
    if end_date:
        query = query.filter(DbEvent.date <= end_date)

    return query.all()



def calculate_seat_layout(total_tickets: int):
    columns = math.isqrt(total_tickets)
    if columns * columns < total_tickets:
        columns += 1
    rows = math.ceil(total_tickets / columns)
    return rows, columns