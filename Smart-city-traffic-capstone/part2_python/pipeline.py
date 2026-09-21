"""End-to-end traffic data cleaning and feature-engineering pipeline."""

import argparse
import logging
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from feature_engineering import create_features
from visualizations import create_visualizations


logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "holiday",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "weather_main",
    "weather_description",
    "date_time",
    "traffic_volume",
]


def configure_logging(log_path: str | Path, debug: bool = False) -> None:
    """Write named-module logs to both the console and a file."""
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    application_logger = logging.getLogger()
    application_logger.handlers.clear()
    application_logger.setLevel(level)
    application_logger.addHandler(file_handler)
    application_logger.addHandler(console_handler)


def load_data(input_path: str | Path) -> pd.DataFrame:
    """Load the raw CSV and report file/parsing errors clearly."""
    try:
        df = pd.read_csv(input_path)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, pd.errors.ParserError):
        logger.error("Unable to load input file: %s", input_path, exc_info=True)
        raise
    logger.info("Raw data loaded successfully: %d rows, %d columns", *df.shape)
    return df


def validate_schema(df: pd.DataFrame) -> None:
    """Validate all expected columns before processing."""
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    logger.info("Schema validated: all %d expected columns are present", len(EXPECTED_COLUMNS))


def _impute_by_month(df: pd.DataFrame, column: str) -> None:
    """Fill missing values with a monthly median, then the global median."""
    missing_before = int(df[column].isna().sum())
    if missing_before == 0:
        logger.info("No values required imputation in %s", column)
        return

    global_median = df[column].median()
    for month in sorted(df["date_time"].dt.month.dropna().unique()):
        month_mask = df["date_time"].dt.month == month
        month_median = df.loc[month_mask, column].median()
        if pd.isna(month_median):
            month_median = global_median
        fill_mask = month_mask & df[column].isna()
        df.loc[fill_mask, column] = month_median

    df[column] = df[column].fillna(global_median)
    logger.warning(
        "Imputed %d invalid or missing %s values using monthly medians",
        missing_before,
        column,
    )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise, parse, de-duplicate and handle impossible values."""
    cleaned = df.copy()

    for column in ["holiday", "weather_main", "weather_description"]:
        cleaned[column] = cleaned[column].fillna("None").astype(str).str.strip()
    cleaned["weather_main"] = cleaned["weather_main"].str.title()
    cleaned["weather_description"] = cleaned["weather_description"].str.lower()
    cleaned["holiday"] = cleaned["holiday"].replace({"nan": "None", "": "None"})
    logger.info("Categorical text values standardised")

    cleaned["date_time"] = pd.to_datetime(cleaned["date_time"], errors="coerce")
    invalid_dates = int(cleaned["date_time"].isna().sum())
    if invalid_dates:
        cleaned = cleaned.dropna(subset=["date_time"])
        logger.warning("Dropped %d rows with invalid date/time values", invalid_dates)
    else:
        logger.info("All date/time values parsed successfully")

    duplicates = int(cleaned.duplicated().sum())
    if duplicates:
        cleaned = cleaned.drop_duplicates().copy()
        logger.warning("Dropped %d fully duplicated rows", duplicates)
    else:
        logger.info("No fully duplicated rows found")

    numerical_columns = ["temp", "rain_1h", "snow_1h", "clouds_all", "traffic_volume"]
    for column in numerical_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    invalid_rules = {
        "temp": (cleaned["temp"] <= 0) | (cleaned["temp"] > 350),
        "rain_1h": (cleaned["rain_1h"] < 0) | (cleaned["rain_1h"] > 9000),
        "snow_1h": (cleaned["snow_1h"] < 0) | (cleaned["snow_1h"] > 1000),
        "traffic_volume": cleaned["traffic_volume"] < 0,
    }
    for column, invalid_mask in invalid_rules.items():
        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            cleaned.loc[invalid_mask, column] = np.nan
            logger.warning("Detected %d impossible values in %s", invalid_count, column)
        else:
            logger.info("No impossible values detected in %s", column)
        _impute_by_month(cleaned, column)

    invalid_clouds = (~cleaned["clouds_all"].between(0, 100)) | cleaned["clouds_all"].isna()
    invalid_cloud_count = int(invalid_clouds.sum())
    if invalid_cloud_count:
        cleaned.loc[invalid_clouds, "clouds_all"] = np.nan
        logger.warning("Detected %d invalid cloud-cover values", invalid_cloud_count)
    _impute_by_month(cleaned, "clouds_all")

    cleaned = cleaned.sort_values("date_time").reset_index(drop=True)
    logger.info("Cleaning complete: %d rows, %d columns", *cleaned.shape)
    return cleaned


def run_pipeline(input_path: str | Path, output_path: str | Path, figures_path: str | Path) -> pd.DataFrame:
    """Run all stages and save the processed data and figures."""
    raw = load_data(input_path)
    validate_schema(raw)
    cleaned = clean_data(raw)
    processed = create_features(cleaned)
    processed.to_csv(output_path, index=False)
    logger.info("Processed data saved: %s", output_path)
    create_visualizations(processed, figures_path)
    logger.info("Pipeline completed successfully")
    return processed


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the traffic analytics pipeline")
    parser.add_argument("--input", default="Metro_Interstate_Traffic_Volume.csv")
    parser.add_argument("--output", default="processed_traffic.csv")
    parser.add_argument("--figures", default="figures")
    parser.add_argument("--log", default="pipeline.log")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    configure_logging(args.log, args.debug)
    try:
        run_pipeline(args.input, args.output, args.figures)
    except (OSError, ValueError, KeyError, pd.errors.ParserError):
        logger.error("Pipeline could not complete", exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
