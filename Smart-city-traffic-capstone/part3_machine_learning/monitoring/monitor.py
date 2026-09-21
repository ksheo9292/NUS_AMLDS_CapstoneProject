"""Basic model-monitoring example."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error


project_folder = Path(__file__).resolve().parents[1]
data = pd.read_csv(project_folder / "data" / "traffic_processed.csv")
model = joblib.load(project_folder / "models" / "traffic_regression_model.joblib")

features = [
    "temp_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "is_holiday",
    "is_weekend",
    "is_low_visibility",
    "is_severe_weather",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
]


# Compare an older period with a recent period
split_row = int(len(data) * 0.80)
old_data = data.iloc[:split_row]
recent_data = data.iloc[split_row:]

old_prediction = model.predict(old_data[features])
recent_prediction = model.predict(recent_data[features])

old_mae = mean_absolute_error(old_data["traffic_volume"], old_prediction)
recent_mae = mean_absolute_error(recent_data["traffic_volume"], recent_prediction)
mae_ratio = recent_mae / old_mae

old_temperature = old_data["temp_celsius"].mean()
recent_temperature = recent_data["temp_celsius"].mean()
temperature_change = abs(recent_temperature - old_temperature)


# Simple alert rules for this classroom simulation
if mae_ratio > 1.50 or temperature_change > 5:
    status = "ALERT"
else:
    status = "PASS"

result = {
    "status": status,
    "old_mae": old_mae,
    "recent_mae": recent_mae,
    "mae_ratio": mae_ratio,
    "old_average_temperature": old_temperature,
    "recent_average_temperature": recent_temperature,
    "temperature_change": temperature_change,
}

output_file = Path(__file__).parent / "monitoring_result.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(result, file, indent=2)

print(result)

