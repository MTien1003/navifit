from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class AQICache(Base):
    __tablename__ = "aqi_cache"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float)
    lng = Column(Float)
    aqi_value = Column(Integer)
    category = Column(String)
    color_code = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)
