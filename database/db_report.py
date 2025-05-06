from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import DbEvent, DbReservation

def total_events(db: Session):
    return db.query(func.count(DbEvent.id)).scalar()

def total_reservations(db: Session):
    return db.query(func.count(DbReservation.id)).scalar()

def total_income(db: Session):
    return db.query(func.sum(DbReservation.quantity)).filter(DbReservation.is_paid == True).scalar() or 0

def total_unpaid_reservations(db: Session):
    return db.query(func.count(DbReservation.id)).filter(DbReservation.is_paid == False).scalar()

def reservations_per_event(db: Session):
    results = db.query(
        DbEvent.title,
        func.count(DbReservation.id).label("reservation_count")
    ).join(DbReservation, DbReservation.event_id == DbEvent.id).group_by(DbEvent.title).all()

    return [{"event_title": title, "reservation_count": count} for title, count in results]

def top_events_by_income(db: Session, limit: int = 5):
    results = db.query(
        DbEvent.title,
        func.sum(DbReservation.quantity).label("total_income")
    ).join(DbReservation, DbReservation.event_id == DbEvent.id).filter(DbReservation.is_paid == True).group_by(DbEvent.title).order_by(func.sum(DbReservation.quantity).desc()).limit(limit).all()

    return [{"event_title": title, "total_income": income} for title, income in results]

def average_income_per_event(db: Session):
    total = total_income(db)
    events_count = total_events(db)
    if events_count == 0:
        return 0
    return total / events_count
