from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Session
from typing import List
from enum import Enum

from beauty_salon_project.shared.auth import get_current_user
from beauty_salon_project.shared.database import Base, get_db, engine
from beauty_salon_project.shared.models import Appointment, AppointmentCreate

app = FastAPI(title="Appointment Service", version="1.0.0")


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentDB(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, index=True)
    service_id = Column(Integer, index=True)
    appointment_date = Column(DateTime)
    status = Column(String, default=AppointmentStatus.PENDING)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


@app.post("/appointments", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate, current_user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    db_appointment = AppointmentDB(
        client_id=current_user["user_id"],
        service_id=appointment.service_id,
        appointment_date=appointment.appointment_date,
        notes=appointment.notes
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return Appointment(
        id=db_appointment.id,
        client_id=db_appointment.client_id,
        service_id=db_appointment.service_id,
        appointment_date=db_appointment.appointment_date,
        status=db_appointment.status,
        notes=db_appointment.notes,
        created_at=db_appointment.created_at
    )


@app.get("/appointments/my", response_model=List[Appointment])
async def get_my_appointments(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    appointments = db.query(AppointmentDB).filter(AppointmentDB.client_id == current_user["user_id"]).all()
    return [Appointment(
        id=app.id,
        client_id=app.client_id,
        service_id=app.service_id,
        appointment_date=app.appointment_date,
        status=app.status,
        notes=app.notes,
        created_at=app.created_at
    ) for app in appointments]


@app.get("/appointments", response_model=List[Appointment])
async def get_all_appointments(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    appointments = db.query(AppointmentDB).all()
    return [Appointment(
        id=app.id,
        client_id=app.client_id,
        service_id=app.service_id,
        appointment_date=app.appointment_date,
        status=app.status,
        notes=app.notes,
        created_at=app.created_at
    ) for app in appointments]


@app.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, current_user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    appointment = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.client_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()

    return {"message": "Appointment cancelled successfully"}