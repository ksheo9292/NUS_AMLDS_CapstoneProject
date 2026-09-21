"""Feature engineering for the traffic analytics pipeline."""

import logging

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


def _z_score(series: pd.Series) -> pd.Series:
    """Return a z-score while safely handling a zero standard deviation."""
    standard_deviation = series.std()
    if standard_deviation == 0 or pd.isna(standard_deviation):
        return pd.Series(0.0, index=series.index)
    return (series - series.mean()) / standard_deviation


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time, weather, numerical and congestion features."""
    logger.info("Dataset shape before feature engineering: %s", df.shape)
    featured = df.copy()

    # Time features
    featured["hour"] = featured["date_time"].dt.hour
    featured["day_of_week"] = featured["date_time"].dt.dayofweek
    featured["month"] = featured["date_time"].dt.month
    featured["year"] = featured["date_time"].dt.year
    featured["is_weekend"] = (featured["day_of_week"] >= 5).astype(int)
    featured["hour_sin"] = np.sin(2 * np.pi * featured["hour"] / 24)
    featured["hour_cos"] = np.cos(2 * np.pi * featured["hour"] / 24)
    featured["day_sin"] = np.sin(2 * np.pi * featured["day_of_week"] / 7)
    featured["day_cos"] = np.cos(2 * np.pi * featured["day_of_week"] / 7)

    # Weather features
    weather_text = (
        featured["weather_main"].fillna("").str.lower()
        + " "
        + featured["weather_description"].fillna("").str.lower()
    )
    featured["is_holiday"] = (featured["holiday"].str.lower() != "none").astype(int)
    featured["has_precipitation"] = (
        (featured["rain_1h"] > 0) | (featured["snow_1h"] > 0)
    ).astype(int)
    featured["is_low_visibility"] = weather_text.str.contains(
        "mist|fog|haze|smoke", regex=True
    ).astype(int)
    featured["is_severe_weather"] = weather_text.str.contains(
        "thunderstorm|squall|tornado|heavy snow|heavy rain", regex=True
    ).astype(int)
    featured["temp_c"] = featured["temp"] - 273.15

    # Scaled numerical features
    featured["temp_z"] = _z_score(featured["temp"])
    featured["clouds_z"] = _z_score(featured["clouds_all"])

    # Fixed traffic bands retained from Part 1.
    featured["traffic_category"] = pd.cut(
        featured["traffic_volume"],
        bins=[-np.inf, 4500, 5500, np.inf],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    # Data-driven quartiles form the ML-ready congestion target.
    q1, q2, q3 = featured["traffic_volume"].quantile([0.25, 0.50, 0.75]).tolist()
    logger.debug("Congestion quartiles: q1=%.2f, q2=%.2f, q3=%.2f", q1, q2, q3)

    def congestion_bucket(value: float) -> str:
        if value <= q1:
            return "Low"
        if value <= q2:
            return "Medium"
        if value <= q3:
            return "High"
        return "Severe"

    featured["congestion_category"] = featured["traffic_volume"].apply(
        congestion_bucket
    )

    weather_dummies = pd.get_dummies(
        featured["weather_main"], prefix="weather", dtype=int
    )
    featured = pd.concat([featured, weather_dummies], axis=1)

    logger.info("Dataset shape after feature engineering: %s", featured.shape)
    return featured
