import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
import random
from typing import Dict, List, Any

class MLService:
    def __init__(self):
        self.model_path = "model.joblib"
        self.model = None
        self.feature_names = ["wind_speed", "temperature", "humidity", "precipitation", "asset_age"]
        self.model_version = "v2.0.0-rf"
        
        # Load model if exists, otherwise train a new one
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print("Loaded existing model.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.train_model()
        else:
            print("No model found. Training new model...")
            self.train_model()

    def train_model(self):
        """
        Generates synthetic historical data based on physics rules and trains a Random Forest.
        """
        # Generate standard synthetic data
        n_samples = 1000
        np.random.seed(42)
        
        data = {
            "wind_speed": np.random.normal(10, 15, n_samples).clip(0, 100),     # mph
            "temperature": np.random.normal(70, 20, n_samples).clip(0, 120),    # F
            "humidity": np.random.normal(50, 20, n_samples).clip(0, 100),       # %
            "precipitation": np.random.exponential(0.1, n_samples),             # inches
            "asset_age": np.random.randint(0, 50, n_samples)                    # years
        }
        
        df = pd.DataFrame(data)

        # Inject "Storm" scenarios (Extreme Weather) to ensure model learns valid high-risk patterns
        # otherwise 80mph is an outlier it has never seen
        n_storm = 200
        storm_data = {
            "wind_speed": np.random.uniform(50, 90, n_storm),
            "temperature": np.random.uniform(90, 110, n_storm),
            "humidity": np.random.uniform(20, 80, n_storm),
            "precipitation": np.random.uniform(0, 2, n_storm),
            "asset_age": np.random.randint(0, 50, n_storm)     
        }
        df_storm = pd.DataFrame(storm_data)
        df = pd.concat([df, df_storm], ignore_index=True)

        # Physics-based outage logic (Ground Truth Generation)
        # Probability increases with high wind, high heat, or old assets
        def calculate_outage_risk(row):
            score = 0
            # Base risks
            if row["wind_speed"] > 40: score += 3
            if row["wind_speed"] > 60: score += 5
            
            # Critical synergy: Old assets die in storms
            if row["wind_speed"] > 50 and row["asset_age"] > 30: score += 8
            
            # New assets are resilient
            if row["asset_age"] < 10: score -= 3
            
            if row["temperature"] > 95: score += 3
            if row["precipitation"] > 1.0: score += 2
            
            # Random chance factor
            prob = 1 / (1 + np.exp(-(score - 6))) # Sigmoid-ish
            return 1 if np.random.random() < prob else 0

        df["outage_occured"] = df.apply(calculate_outage_risk, axis=1)
        
        # Train Model
        X = df[self.feature_names]
        y = df["outage_occured"]
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        joblib.dump(self.model, self.model_path)
        print("Model trained and saved.")

    def predict_outage_probability(self, feeder_id: str, weather_data: Dict[str, float]) -> float:
        """
        Predict probability using the trained model.
        """
        if not self.model:
            return 0.0
            
        # Mock asset data (in real app, fetch from Asset DB)
        # Hash feeder ID to get a deterministic "age" for this demo
        asset_age = int(feeder_id.replace("F-", "")) % 50 
        
        input_data = pd.DataFrame([{
            "wind_speed": weather_data.get("wind_speed", 0),
            "temperature": weather_data.get("temperature", 70),
            "humidity": weather_data.get("humidity", 50),
            "precipitation": weather_data.get("precipitation", 0),
            "asset_age": asset_age
        }])
        
        # Ensure column order matches training
        input_data = input_data[self.feature_names]
        
        # Predict probability of class 1 (Outage)
        prob = self.model.predict_proba(input_data)[0][1]
        return float(prob)

    def estimate_restoration_time(self, feeder_id: str, severity: str) -> float:
        """
        Rule-based ETR estimation.
        """
        base_time = 0
        if severity == "critical": base_time = 240 # 4 hours
        elif severity == "high": base_time = 120   # 2 hours
        elif severity == "moderate": base_time = 60 # 1 hour
        else: return 0
        
        return base_time + random.randint(-30, 30)

    def get_contributing_factors(self, feeder_id: str) -> List[Dict[str, Any]]:
        """
        Returns feature importance for the prediction (mocked for now based on global model importance).
        """
        if not self.model:
            return []
            
        importances = self.model.feature_importances_
        factors = []
        for name, imp in zip(self.feature_names, importances):
            factors.append({"feature": name, "importance": float(imp)})
            
        return sorted(factors, key=lambda x: x["importance"], reverse=True)[:3]

ml_service = MLService()
