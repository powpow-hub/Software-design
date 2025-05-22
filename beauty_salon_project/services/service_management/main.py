from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import Session
from typing import List


from beauty_salon_project.shared.auth import get_current_user
from beauty_salon_project.shared.database import Base, get_db, engine
from beauty_salon_project.shared.models import Service, ServiceCreate

app = FastAPI(title="Service Management", version="1.0.0")


class ServiceDB(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    duration_minutes = Column(Integer)
    specialist_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


@app.post("/services", response_model=Service)
async def create_service(service: ServiceCreate, current_user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_service = ServiceDB(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return Service(
        id=db_service.id,
        name=db_service.name,
        description=db_service.description,
        price=db_service.price,
        duration_minutes=db_service.duration_minutes,
        specialist_type=db_service.specialist_type,
        created_at=db_service.created_at
    )


@app.get("/services", response_model=List[Service])
async def get_services(db: Session = Depends(get_db)):
    services = db.query(ServiceDB).all()
    return [Service(
        id=service.id,
        name=service.name,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        specialist_type=service.specialist_type,
        created_at=service.created_at
    ) for service in services]


@app.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return Service(
        id=service.id,
        name=service.name,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        specialist_type=service.specialist_type,
        created_at=service.created_at
    )


@app.put("/services/{service_id}", response_model=Service)
async def update_service(service_id: int, service: ServiceCreate, current_user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_service = db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    for key, value in service.dict().items():
        setattr(db_service, key, value)

    db.commit()
    db.refresh(db_service)

    return Service(
        id=db_service.id,
        name=db_service.name,
        description=db_service.description,
        price=db_service.price,
        duration_minutes=db_service.duration_minutes,
        specialist_type=db_service.specialist_type,
        created_at=db_service.created_at
    )


@app.delete("/services/{service_id}")
async def delete_service(service_id: int, current_user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_service = db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(db_service)
    db.commit()

    return {"message": "Service deleted successfully"}