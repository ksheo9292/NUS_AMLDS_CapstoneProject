"""Small command-line application for querying processed traffic data."""

import argparse
import logging
from pathlib import Path
import sys

import pandas as pd


logger = logging.getLogger(__name__)


def configure_logging(log_path: str | Path) -> None:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    application_logger = logging.getLogger()
    application_logger.handlers.clear()
    application_logger.setLevel(logging.INFO)
    application_logger.addHandler(file_handler)
    application_logger.addHandler(console_handler)


def load_processed_data(path: str | Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, parse_dates=["date_time"])
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, pd.errors.ParserError):
        logger.error("Could not load processed data: %s", path)
        raise
    logger.info("Processed data loaded: %d rows, %d columns", *df.shape)
    return df


def query_datetime(df: pd.DataFrame, value: str) -> str:
    try:
        requested = pd.to_datetime(value, format="%Y-%m-%d %H:%M")
    except ValueError as error:
        raise ValueError("Use date/time format YYYY-MM-DD HH:MM") from error
    matches = df[df["date_time"] == requested]
    if matches.empty:
        return f"No traffic record found for {requested:%Y-%m-%d %H:%M}."
    result = matches[["date_time", "traffic_volume", "weather_main", "temp_c"]]
    return result.to_string(index=False)


def high_traffic(df: pd.DataFrame, threshold: int, limit: int) -> str:
    result = (
        df[df["traffic_volume"] > threshold]
        .nlargest(limit, "traffic_volume")
        [["date_time", "traffic_volume", "weather_main"]]
    )
    return result.to_string(index=False) if not result.empty else "No matching periods found."


def compare_day_types(df: pd.DataFrame) -> str:
    comparison = df.assign(
        day_type=df["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    ).groupby("day_type")["traffic_volume"].mean()
    return comparison.round(1).to_string()


def recommend_window(df: pd.DataFrame, day_type: str, weather: str | None) -> str:
    weekend_value = 1 if day_type == "weekend" else 0
    filtered = df[(df["is_weekend"] == weekend_value) & df["hour"].between(6, 22)]
    if weather:
        filtered = filtered[filtered["weather_main"].str.lower() == weather.lower()]
    if filtered.empty:
        return "No records match the requested conditions."
    hourly = filtered.groupby("hour")["traffic_volume"].mean()
    best_hour = int(hourly.idxmin())
    condition = f" in {weather} weather" if weather else ""
    return (
        f"Recommended {day_type} travel window{condition}: "
        f"{best_hour:02d}:00-{(best_hour + 1):02d}:00 "
        f"(historical average {hourly.loc[best_hour]:,.0f} vehicles)."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query processed traffic data")
    parser.add_argument("--data", default="processed_traffic.csv")
    parser.add_argument("--log", default="pipeline.log")
    subparsers = parser.add_subparsers(dest="command", required=True)

    date_parser = subparsers.add_parser("datetime", help="Query a date and time")
    date_parser.add_argument("value", help='Example: "2017-09-30 12:00"')

    high_parser = subparsers.add_parser("high-traffic", help="List high-traffic periods")
    high_parser.add_argument("--threshold", type=int, default=5500)
    high_parser.add_argument("--limit", type=int, default=10)

    subparsers.add_parser("compare", help="Compare weekday and weekend traffic")

    recommend_parser = subparsers.add_parser("recommend", help="Recommend a travel time")
    recommend_parser.add_argument("--day-type", choices=["weekday", "weekend"], default="weekday")
    recommend_parser.add_argument("--weather", help='Optional, for example "Clear"')
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.log)
    logger.info("CLI command invoked: %s; arguments: %s", args.command, vars(args))
    try:
        df = load_processed_data(args.data)
        if args.command == "datetime":
            answer = query_datetime(df, args.value)
        elif args.command == "high-traffic":
            answer = high_traffic(df, args.threshold, args.limit)
        elif args.command == "compare":
            answer = compare_day_types(df)
        else:
            answer = recommend_window(df, args.day_type, args.weather)
        print(answer)
        return 0
    except (OSError, ValueError, KeyError) as error:
        logger.error("Command failed: %s", error)
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
