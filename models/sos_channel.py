import enum
from sqlalchemy import Column, Integer, String, Enum
from database import Base

class SOSType(enum.Enum):
    police = "police"
    hospital = "hospital"
    embassy = "embassy"
    other = "other"

class SOSChannel(Base):
    __tablename__ = "sos_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    name_ja = Column(String)
    phone = Column(String)
    type = Column(Enum(SOSType))
