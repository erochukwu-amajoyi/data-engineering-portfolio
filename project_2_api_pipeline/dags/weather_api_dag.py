from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from api_pipeline import run_pipeline  # noqa: E402


DEFAULT_ARGS = {
    "owner": "data-engineering-portfolio",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="weather_api_ingestion",
    description="Fetch current weather data from an API and load it into Postgres.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["portfolio", "api", "weather"],
)
def weather_api_ingestion():
    @task()
    def run_weather_pipeline():
        run_pipeline()

    run_weather_pipeline()


weather_api_ingestion()

