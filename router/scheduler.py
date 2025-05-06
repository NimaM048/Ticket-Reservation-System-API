from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import DbSeatReservation



def check_expired_reservations():
    db: Session = next(get_db())
    try:
        now = datetime.now(timezone.utc)
        expired_reservations = db.query(DbSeatReservation).filter(
            DbSeatReservation.expires_at <= now,
            DbSeatReservation.is_paid == False,
            DbSeatReservation.is_canceled == False
        ).all()

        for reservation in expired_reservations:

            if reservation.seat.is_reserved:
                reservation.is_canceled = True
                reservation.seat.is_reserved = False
                reservation.event.available_tickets += 1


                reservation.reservation.quantity = max(0, reservation.reservation.quantity - 1)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error checking expired reservations: {e}")
    finally:
        db.close()