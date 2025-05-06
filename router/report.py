from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.authentication import oauth2_scheme
from database.db_report import (
    total_events,
    total_reservations,
    total_income,
    total_unpaid_reservations,
    reservations_per_event,
    top_events_by_income,
    average_income_per_event,
)
from database.db import get_db

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get("/total-events")
def get_total_events_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"total_events": total_events(db)}

@router.get("/total-reservations")
def get_total_reservations_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"total_reservations": total_reservations(db)}

@router.get("/total-income")
def get_total_income_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"total_income": total_income(db)}

@router.get("/total-unpaid-reservations")
def get_total_unpaid_reservations_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"total_unpaid_reservations": total_unpaid_reservations(db)}

@router.get("/reservations-per-event")
def get_reservations_per_event_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"reservations_per_event": reservations_per_event(db)}

@router.get("/top-events-by-income")
def get_top_events_by_income_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"top_events_by_income": top_events_by_income(db)}

@router.get("/average-income-per-event")
def get_average_income_per_event_report(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return {"average_income_per_event": average_income_per_event(db)}
