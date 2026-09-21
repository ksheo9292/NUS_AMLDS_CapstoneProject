"""Basic travel-time recommendation system."""

from pathlib import Path

import pandas as pd


project_folder = Path(__file__).resolve().parents[1]
data = pd.read_csv(project_folder / "data" / "traffic_processed.csv")


def recommend_travel_time(day_type="Weekday", weather="Clear"):
    selected_data = data[data["weather_main"] == weather].copy()

    if day_type == "Weekend":
        selected_data = selected_data[selected_data["is_weekend"] == 1]
    else:
        selected_data = selected_data[selected_data["is_weekend"] == 0]

    hourly_average = selected_data.groupby("hour")["traffic_volume"].mean()
    best_hours = hourly_average.sort_values().head(3)

    print(f"Recommended travel times for {day_type} and {weather} weather:")
    for hour, traffic in best_hours.items():
        next_hour = (hour + 1) % 24
        print(f"{hour:02d}:00 to {next_hour:02d}:00 - average traffic {traffic:.0f}")

    return best_hours


if __name__ == "__main__":
    recommend_travel_time("Weekday", "Clear")

