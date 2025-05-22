from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration_minutes: int
    specialist_type: Optional[str] = None

class Service(ServiceCreate):
    id: int
    created_at: datetime

class AppointmentCreate(BaseModel):
    service_id: int
    appointment_date: datetime
    notes: Optional[str] = None

class Appointment(AppointmentCreate):
    id: int
    client_id: int
    status: str
    created_at: datetime

class ReviewCreate(BaseModel):
    service_id: int
    rating: int
    comment: Optional[str] = None

class Review(ReviewCreate):
    id: int
    client_id: int
    created_at: datetime