from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class BestTime(Base):
    __tablename__ = "best_times"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id"))
    day_of_week = Column(Integer) # 0-6 (0 là thứ 2 hoặc CN tuỳ quy ước)
    hour = Column(Integer) # 0-23
    score = Column(Integer) # 0-100
