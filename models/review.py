from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id"))
    user_name = Column(String)
    rating = Column(Integer)  # 1-5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
