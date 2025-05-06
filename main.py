from fastapi import FastAPI, status
from enum import Enum
from typing import Optional
from auth import authentication
from database.db import engine
from router import user, events, reservations, admin, report, hall, sear_reservation, seat, payment_reservation
from database import models
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from router.scheduler import check_expired_reservations

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Include routers
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(events.router)
app.include_router(reservations.router)
app.include_router(admin.router)
app.include_router(report.router)
app.include_router(hall.router)
app.include_router(seat.router)
app.include_router(sear_reservation.router)
app.include_router(payment_reservation.router)

# Setup scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(check_expired_reservations, 'interval', seconds=60)
scheduler.start()

# Ensure scheduler shuts down properly
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
