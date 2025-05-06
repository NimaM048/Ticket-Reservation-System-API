from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime

class DbUsers(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    reservations = relationship('DbReservation', back_populates='user')


class DbEvent(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    date = Column(DateTime)
    location = Column(String)
    total_tickets = Column(Integer)
    available_tickets = Column(Integer)
    hall_id = Column(Integer, ForeignKey('halls.id'))


    hall = relationship('DbHall', back_populates='events')
    reservations = relationship('DbReservation', back_populates='event')


class DbHall(Base):
    __tablename__ = 'halls'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_rows = Column(Integer, nullable=False)
    total_columns = Column(Integer, nullable=False)
    total_seats = Column(Integer, nullable=False)


    events = relationship('DbEvent', back_populates='hall', cascade="all, delete-orphan")
    seats = relationship('DbSeat', back_populates='hall', cascade="all, delete-orphan")

class DbSeat(Base):
    __tablename__ = 'seats'
    id = Column(Integer, primary_key=True, index=True)
    hall_id = Column(Integer, ForeignKey('halls.id'), nullable=False)
    row = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    seat_type = Column(String, default='NORMAL')
    is_reserved = Column(Boolean, default=False)

    hall = relationship('DbHall', back_populates='seats')
    seat_reservations = relationship('DbSeatReservation', back_populates='seat', cascade="all, delete-orphan")


class DbSeatReservation(Base):
    __tablename__ = 'seat_reservations'
    id = Column(Integer, primary_key=True, index=True)
    seat_id = Column(Integer, ForeignKey('seats.id'), nullable=False)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    is_paid = Column(Boolean, default=False)
    reserved_at = Column(DateTime(timezone=True), server_default=func.now())
    is_canceled = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True))


    seat = relationship('DbSeat', back_populates='seat_reservations')
    reservation = relationship('DbReservation', back_populates='seat_reservations')
    event = relationship('DbEvent')



class DbReservation(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    is_paid = Column(Boolean, default=False)
    quantity = Column(Integer, default=1)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_canceled = Column(Boolean, default=False)
    payment_time = Column(DateTime(timezone=True), nullable=True)

    user = relationship('DbUsers', back_populates='reservations')
    event = relationship('DbEvent', back_populates='reservations')
    seat_reservations = relationship('DbSeatReservation',
                                     back_populates='reservation',
                                     cascade="all, delete-orphan")