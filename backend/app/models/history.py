from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    feeder_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    outage_probability = Column(Float)
    weather_data = Column(JSON) # Store snapshot of weather
    prediction_result = Column(JSON) # Store full result including severity, ETR
