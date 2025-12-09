from sqlalchemy import Column, Integer, String, Float
from .base import Base

class Feeder(Base):
    __tablename__ = "feeders"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    location_lat = Column(Float)
    location_lng = Column(Float)
    customer_count = Column(Integer)
    asset_count = Column(Integer)
