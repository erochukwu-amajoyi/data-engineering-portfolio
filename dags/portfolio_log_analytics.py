from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_7_log_pipeline")
from log_pipeline import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_log_analytics_incremental",
    description="Parse application logs incrementally and build analytics marts.",
    start_date=datetime(2025, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "logs", "incremental"],
)
def portfolio_log_analytics_incremental():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_log_analytics_incremental()

