from pydantic import BaseModel
from typing import Optional

class FeederBase(BaseModel):
    id: str
    name: str
    location_lat: float
    location_lng: float
    customer_count: int
    asset_count: int

class FeederCreate(FeederBase):
    pass

class Feeder(FeederBase):
    class Config:
        from_attributes = True
