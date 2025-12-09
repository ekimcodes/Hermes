from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from .base import Base

class Outage(Base):
    __tablename__ = "outages"

    id = Column(String, primary_key=True, index=True)
    feeder_id = Column(String, ForeignKey("feeders.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    cause = Column(String)
    affected_customers = Column(Integer)
    status = Column(String) # Active, Restored
