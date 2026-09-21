"""Basic FastAPI model deployment."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


project_folder = Path(__file__).resolve().parents[1]
model = joblib.load(project_folder / "models" / "traffic_regression_model.joblib")

app = FastAPI(title="Basic Traffic Prediction API")


class TrafficInput(BaseModel):
    hour: int
    day_of_week: int
    temp_celsius: float = 15
    rain_1h: float = 0
    snow_1h: float = 0
    clouds_all: float = 40
    is_holiday: int = 0
    is_low_visibility: int = 0
    is_severe_weather: int = 0


@app.get("/")
def home():
    return {"message": "Traffic prediction API is running"}


@app.post("/predict")
def predict_traffic(user_input: TrafficInput):
    hour_sin = np.sin(2 * np.pi * user_input.hour / 24)
    hour_cos = np.cos(2 * np.pi * user_input.hour / 24)
    dow_sin = np.sin(2 * np.pi * user_input.day_of_week / 7)
    dow_cos = np.cos(2 * np.pi * user_input.day_of_week / 7)

    input_table = pd.DataFrame(
        [
            {
                "temp_celsius": user_input.temp_celsius,
                "rain_1h": user_input.rain_1h,
                "snow_1h": user_input.snow_1h,
                "clouds_all": user_input.clouds_all,
                "is_holiday": user_input.is_holiday,
                "is_weekend": int(user_input.day_of_week >= 5),
                "is_low_visibility": user_input.is_low_visibility,
                "is_severe_weather": user_input.is_severe_weather,
                "hour_sin": hour_sin,
                "hour_cos": hour_cos,
                "dow_sin": dow_sin,
                "dow_cos": dow_cos,
            }
        ]
    )

    prediction = model.predict(input_table)[0]
    return {"predicted_traffic_volume": round(float(prediction), 1)}

