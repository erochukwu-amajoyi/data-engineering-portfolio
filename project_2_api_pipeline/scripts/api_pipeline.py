import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API_URL = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=26.7&longitude=88.4&current_weather=true"
)
logger = logging.getLogger(__name__)


def configure_logging():
    if logging.getLogger().handlers:
        return

    log_dir = PROJECT_ROOT / "logs"
    try:
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "pipeline.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    except OSError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logger.warning("File logging unavailable; using console logging instead")


def extract_data(url=None, timeout=10):
    url = url or os.getenv("WEATHER_API_URL", DEFAULT_API_URL)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    logger.info("Fetched API data from %s", url)
    return response.json()


def transform_data(data):
    if "current_weather" not in data:
        raise ValueError("API payload is missing current_weather")

    current = data["current_weather"]
    required_fields = {"temperature", "windspeed", "winddirection", "time"}
    missing_fields = sorted(required_fields - set(current))
    if missing_fields:
        raise ValueError(f"API payload is missing fields: {', '.join(missing_fields)}")

    df = pd.DataFrame(
        [
            {
                "temperature": current["temperature"],
                "windspeed": current["windspeed"],
                "winddirection": current["winddirection"],
                "observation_time": current["time"],
            }
        ]
    )
    df["observation_time"] = pd.to_datetime(df["observation_time"], errors="raise")
    logger.info("Transformed API payload into %s row", len(df))
    return df


def load_data(df, database_url=None, table_name=None, if_exists=None):
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/data_projects",
    )
    table_name = table_name or os.getenv("WEATHER_TABLE_NAME", "weather_data")
    if_exists = if_exists or os.getenv("WEATHER_LOAD_MODE", "append")

    engine = create_engine(database_url)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.info("Loaded %s weather rows into %s", len(df), table_name)


def run_pipeline(dry_run=False):
    configure_logging()
    data = extract_data()
    df = transform_data(data)

    if dry_run:
        print(df.to_string(index=False))
        logger.info("Dry run completed successfully")
        return df

    load_data(df)
    logger.info("API pipeline executed successfully")
    return df


def parse_args():
    parser = argparse.ArgumentParser(description="Run the resilient weather API pipeline.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and transform data without loading it to Postgres.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(dry_run=args.dry_run)
