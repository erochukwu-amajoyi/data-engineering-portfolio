from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_2_api_pipeline")
from api_pipeline import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_weather_api_ingestion",
    description="Run the weather API ingestion pipeline.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 3, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "api", "weather"],
)
def portfolio_weather_api_ingestion():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_weather_api_ingestion()

