from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import random

from app.core.database import SessionLocal, engine, Base
from app.services.weather_service import weather_service
from app.services.ml_service import ml_service
from app.models.history import PredictionHistory

# Ensure table exists
Base.metadata.create_all(bind=engine)

class IngestionService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        # Run every 15 minutes
        self.scheduler.add_job(self.collect_data, 'interval', minutes=15)
        self.scheduler.start()
        print("Ingestion Service started. Job scheduled every 15 minutes.")

    async def collect_data(self):
        print(f"[{datetime.now()}] Starting data collection job...")
        db = SessionLocal()
        try:
            # 1. Defined Feeder List (Same as Dashboard)
            # In a real app, fetches from Asset DB
            feeder_ids = [f"F-{1000 + i}" for i in range(200)]
            
            # 2. Mock Locations (Bay Area)
            base_lat = 37.8
            base_lon = -122.3
            feeder_locations = []
            for fid in feeder_ids:
                seed = int(fid.replace("F-", ""))
                random.seed(seed)
                lat = base_lat + random.uniform(-0.1, 0.1)
                lon = base_lon + random.uniform(-0.1, 0.1)
                feeder_locations.append((fid, lat, lon))

            # 3. Batch Fetch Weather
            lats = [loc[1] for loc in feeder_locations]
            lons = [loc[2] for loc in feeder_locations]
            weather_results = await weather_service.get_current_weather_batch(lats, lons)

            # 4. Predict & Store
            new_records = []
            for i, (fid, _, _) in enumerate(feeder_locations):
                w_data = weather_results[i]
                prob = ml_service.predict_outage_probability(fid, w_data)
                
                # Create History Record
                record = PredictionHistory(
                    feeder_id=fid,
                    outage_probability=prob,
                    weather_data=w_data,
                    prediction_result={
                        "severity": "critical" if prob > 0.7 else "high" if prob > 0.5 else "moderate" if prob > 0.3 else "low",
                        "wind_speed": w_data.get("wind_speed")
                    }
                )
                new_records.append(record)
            
            # Bulk Insert
            db.add_all(new_records)
            db.commit()
            print(f"[{datetime.now()}] Successfully saved {len(new_records)} records to database.")

        except Exception as e:
            print(f"Error in collection job: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    # Standalone execution for testing
    service = IngestionService()
    asyncio.run(service.collect_data())
