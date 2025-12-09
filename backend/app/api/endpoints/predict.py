from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import random
from ...schemas.prediction import PredictionRequest, PredictionResponse, PredictionResponseItem, ContributingFactor
from ...services.ml_service import ml_service
from ...services.weather_service import weather_service

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_outages(request: PredictionRequest):
    predictions = []
    
    # Bay Area generic coordinates for demo
    base_lat = 37.8
    base_lon = -122.3
    
    # 1. Pre-calculate all coordinates
    feeder_locations = []
    for feeder_id in request.feeder_ids:
        seed = int(feeder_id.replace("F-", ""))
        random.seed(seed)
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        feeder_locations.append((feeder_id, lat, lon))
    
    # 2. Batch fetch weather for ALL feeders in one go
    lats = [loc[1] for loc in feeder_locations]
    lons = [loc[2] for loc in feeder_locations]
    
    # This is the optimization: 1 HTTP Request instead of 200
    weather_results = await weather_service.get_current_weather_batch(lats, lons)
    
    # 3. Process predictions
    for i, (feeder_id, _, _) in enumerate(feeder_locations):
        weather_data = weather_results[i]
        
        if request.weather_override:
            weather_data.update(request.weather_override)
        
        # Predict probability using TRAINED ML Model
        prob = ml_service.predict_outage_probability(feeder_id, weather_data)
        
        # Determine severity based on probability
        severity = "low"
        if prob > 0.7:
            severity = "critical"
        elif prob > 0.5:
            severity = "high"
        elif prob > 0.3:
            severity = "moderate"
            
        etr = ml_service.estimate_restoration_time(feeder_id, severity) if prob > 0.3 else 0
        
        # Convert dict factors to Pydantic models
        raw_factors = ml_service.get_contributing_factors(feeder_id)
        contributing_factors = [
            ContributingFactor(feature=f["feature"], importance=f["importance"]) 
            for f in raw_factors
        ]

        predictions.append(PredictionResponseItem(
            feeder_id=feeder_id,
            timestamp=request.timestamp or datetime.now(),
            outage_probability=prob,
            etr_minutes=etr,
            severity=severity,
            wind_speed=weather_data.get("wind_speed", 0.0),
            top_contributing_factors=contributing_factors
        ))
        
    return PredictionResponse(
        predictions=predictions,
        model_version=ml_service.model_version
    )
