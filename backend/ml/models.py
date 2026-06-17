"""GRIDSENTINEL — ML Models for Grid Intelligence"""

import numpy as np
import pandas as pd
from typing import Dict, Any

# Mock XGBoost model (for hackathon demo purposes)
# In a real environment, we'd use xgboost.XGBClassifier loaded from joblib

class FailurePredictor:
    def __init__(self):
        self.model_loaded = True
        
    def predict_failure_probability(self, features: Dict[str, float]) -> float:
        """
        Predict failure probability for a component based on features.
        Features typically include: loading_pct, temperature_c, age_years,
        maintenance_gap_days, weather_stress_index.
        """
        # Feature extraction with defaults
        loading = features.get('loading_pct', 50)
        temp = features.get('temperature_c', 40)
        age = features.get('age_years', 10)
        
        # Synthetic risk calculation based on XGBoost feature importance patterns
        risk = 0.0
        
        # Loading is non-linear risk factor
        if loading > 120:
            risk += 0.6
        elif loading > 100:
            risk += 0.3
        elif loading > 80:
            risk += 0.1
            
        # Temperature is critical
        if temp > 85:
            risk += 0.5
        elif temp > 75:
            risk += 0.2
            
        # Age increases baseline risk
        risk += (age / 100) * 0.1
        
        # Cap at 0.99
        return min(0.99, risk)
        
    def predict_time_to_failure(self, features: Dict[str, float]) -> float:
        """Estimate hours until component failure based on current stress."""
        prob = self.predict_failure_probability(features)
        
        if prob < 0.05:
            return 720.0 # 1 month+
        elif prob < 0.2:
            return 168.0 # 1 week
        elif prob < 0.5:
            return 48.0 # 2 days
        elif prob < 0.8:
            return 12.0 # Half day
        else:
            return max(1.0, 12.0 * (1.0 - prob))


class DemandForecaster:
    def __init__(self):
        self.model_loaded = True
        
    def forecast_24h(self, city: str, current_demand: float, temperature: float) -> list:
        """Forecast demand for the next 24 hours."""
        forecast = []
        base = current_demand
        
        # Simple daily profile (peaking at evening)
        for hour in range(24):
            # Time of day factor (0-23)
            # Assuming current time is hour 0 of the forecast
            tod = (datetime.now().hour + hour) % 24
            
            tod_factor = 1.0
            if 18 <= tod <= 22:  # Evening peak
                tod_factor = 1.25
            elif 10 <= tod <= 17:  # Day peak
                tod_factor = 1.15
            elif 2 <= tod <= 5:  # Night trough
                tod_factor = 0.7
                
            # Temp factor
            temp_factor = 1.0 + max(0, (temperature - 30) * 0.02)
            
            # Add some noise
            noise = np.random.normal(1.0, 0.02)
            
            val = base * tod_factor * temp_factor * noise
            forecast.append({
                "hour_offset": hour,
                "predicted_mw": round(val, 1)
            })
            
        return forecast

# Global instances
failure_model = FailurePredictor()
demand_model = DemandForecaster()
