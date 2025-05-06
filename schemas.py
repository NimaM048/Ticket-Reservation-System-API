from typing import List, Optional
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        orm_mode = True



class User(UserBase):

    id : int
    username : str


    class Config:
        orm_mode = True




class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    location: str
    total_tickets: int
    available_tickets: int
    hall_id: Optional[int] = None

    class Config:
        orm_mode = True

class EventDisplay(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    location: str
    total_tickets: int
    available_tickets: int

    class Config:
        orm_mode = True



class ReservationBase(BaseModel):
    event_id: int
    quantity: int = 1

class ReservationDisplay(BaseModel):
    id: int
    user_id: int
    event_id: int
    quantity: int
    timestamp: datetime
    is_paid: bool
    payment_time: datetime | None = None
    is_canceled: bool

    class Config:
        orm_mode = True



class HallBase(BaseModel):
    name: str
    total_seats: int

class HallCreate(BaseModel):
    name: str
    total_rows: int
    total_columns: int

    @property
    def total_seats(self):
        return self.total_rows * self.total_columns


class HallDisplay(BaseModel):
    id: int
    name: str
    total_rows: int
    total_columns: int


class HallResponse(HallBase):
    id: int

    class Config:
        orm_mode = True



class SeatCreate(BaseModel):
    hall_id: int
    row: int
    number: int
    seat_type: str = "NORMAL"
    is_reserved: bool = False

class SeatDisplay(BaseModel):
    id: int
    hall_id: int
    row: int
    number: int
    seat_type: str
    is_reserved: bool

    class Config:
        orm_mode = True


class SeatReservationCreate(BaseModel):
    seat_ids: List[int]
    event_id: int
    is_paid: bool = False


class SeatReservationDisplay(BaseModel):
    id: int
    seat_id: int
    reservation_id: int
    event_id: int
    is_paid: bool
    reserved_at: datetime

    class Config:
        orm_mode = True


class BulkSeatTypeUpdate(BaseModel):
    seat_ids: List[int]
    new_seat_type: str
