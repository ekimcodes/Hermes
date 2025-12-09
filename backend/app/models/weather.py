from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from .base import Base

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    feeder_id = Column(String, ForeignKey("feeders.id"))
    timestamp = Column(DateTime)
    temperature = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
