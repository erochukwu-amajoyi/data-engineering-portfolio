from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_4_json_pipeline")
from json_pipeline import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_json_order_normalization",
    description="Normalize nested JSON orders into relational tables.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "json", "normalization"],
)
def portfolio_json_order_normalization():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_json_order_normalization()

