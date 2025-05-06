# router/payment.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_db
import random

from database.models import DbSeatReservation

router = APIRouter(prefix="/payment", tags=["Payment"])


@router.post("/{reservation_id}/pay")
def process_payment(reservation_id: int, db: Session = Depends(get_db)):

    reservations = db.query(DbSeatReservation).filter(
        DbSeatReservation.reservation_id == reservation_id,
        DbSeatReservation.is_canceled == False
    ).all()

    if not reservations:
        raise HTTPException(status_code=404, detail="No active reservations found")

    payment_success = random.choice([True, False])

    if payment_success:
        for reservation in reservations:
            reservation.is_paid = True
            reservation.expires_at = None
        db.commit()
        return {"message": "پرداخت موفقیت‌آمیز بود ✅"}
    else:
        return {"message": "پرداخت ناموفق بود ❌ لطفا دوباره تلاش کنید"}