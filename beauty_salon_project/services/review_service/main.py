from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Session
from typing import List


from beauty_salon_project.shared.auth import get_current_user
from beauty_salon_project.shared.database import Base, get_db, engine
from beauty_salon_project.shared.models import Review, ReviewCreate

app = FastAPI(title="Review Service", version="1.0.0")


class ReviewDB(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, index=True)
    service_id = Column(Integer, index=True)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


@app.post("/reviews", response_model=Review)
async def create_review(review: ReviewCreate, current_user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    db_review = ReviewDB(
        client_id=current_user["user_id"],
        service_id=review.service_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return Review(
        id=db_review.id,
        client_id=db_review.client_id,
        service_id=db_review.service_id,
        rating=db_review.rating,
        comment=db_review.comment,
        created_at=db_review.created_at
    )


@app.get("/reviews/service/{service_id}", response_model=List[Review])
async def get_service_reviews(service_id: int, db: Session = Depends(get_db)):
    reviews = db.query(ReviewDB).filter(ReviewDB.service_id == service_id).all()
    return [Review(
        id=review.id,
        client_id=review.client_id,
        service_id=review.service_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    ) for review in reviews]


@app.get("/reviews", response_model=List[Review])
async def get_all_reviews(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    reviews = db.query(ReviewDB).all()
    return [Review(
        id=review.id,
        client_id=review.client_id,
        service_id=review.service_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    ) for review in reviews]


@app.delete("/reviews/{review_id}")
async def delete_review(review_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    review = db.query(ReviewDB).filter(ReviewDB.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted successfully"}