from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_6_ecommerce_pipeline")
from ecommerce_pipeline import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_ecommerce_analytics",
    description="Build e-commerce analytics marts.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "ecommerce", "analytics"],
)
def portfolio_ecommerce_analytics():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_ecommerce_analytics()

