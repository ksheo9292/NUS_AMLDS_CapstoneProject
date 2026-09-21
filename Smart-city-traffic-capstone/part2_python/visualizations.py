"""Matplotlib visualisations for the traffic analytics pipeline."""

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


logger = logging.getLogger(__name__)


def _save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Figure saved: %s", path)


def create_visualizations(df: pd.DataFrame, output_directory: str | Path) -> list[Path]:
    """Create four figures and return their paths."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    hourly = df.groupby("hour")["traffic_volume"].mean()
    path = output_directory / "01_traffic_by_hour.png"
    hourly.plot(marker="o", color="#1f77b4", figsize=(8, 4))
    plt.title("Average Traffic Volume by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Average traffic volume")
    plt.grid(alpha=0.25)
    _save_figure(path)
    paths.append(path)

    day_type = df.assign(
        day_type=df["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    ).groupby("day_type")["traffic_volume"].mean()
    path = output_directory / "02_weekday_vs_weekend.png"
    day_type.reindex(["Weekday", "Weekend"]).plot(
        kind="bar", color=["#2ca02c", "#ff7f0e"], figsize=(6, 4)
    )
    plt.title("Average Weekday vs Weekend Traffic")
    plt.xlabel("")
    plt.ylabel("Average traffic volume")
    plt.xticks(rotation=0)
    _save_figure(path)
    paths.append(path)

    weather = df.groupby("weather_main")["traffic_volume"].mean().sort_values()
    path = output_directory / "03_traffic_by_weather.png"
    weather.plot(kind="barh", color="#9467bd", figsize=(8, 5))
    plt.title("Average Traffic Volume by Weather")
    plt.xlabel("Average traffic volume")
    plt.ylabel("Weather")
    _save_figure(path)
    paths.append(path)

    sample = df.sample(min(5000, len(df)), random_state=42)
    path = output_directory / "04_temperature_vs_traffic.png"
    plt.figure(figsize=(8, 4.5))
    plt.scatter(sample["temp_c"], sample["traffic_volume"], alpha=0.25, s=10)
    plt.title("Temperature vs Traffic Volume")
    plt.xlabel("Temperature (Celsius)")
    plt.ylabel("Traffic volume")
    _save_figure(path)
    paths.append(path)

    return paths
