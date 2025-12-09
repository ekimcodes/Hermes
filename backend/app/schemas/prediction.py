from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class PredictionRequest(BaseModel):
    feeder_ids: List[str]
    timestamp: Optional[datetime] = None
    weather_override: Optional[Dict[str, float]] = None

class OUTAGE_CONFIDENCE(BaseModel):
    low: float
    high: float

class ContributingFactor(BaseModel):
    feature: str
    importance: float

class PredictionResponseItem(BaseModel):
    feeder_id: str
    timestamp: datetime
    outage_probability: float
    etr_minutes: Optional[float]
    severity: str
    wind_speed: float
    top_contributing_factors: List[ContributingFactor]

class PredictionResponse(BaseModel):
    predictions: List[PredictionResponseItem]
    model_version: str
