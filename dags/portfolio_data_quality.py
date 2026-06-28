from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_3_data_cleaning")
from cleaning_pipeline import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_sales_data_quality",
    description="Run the sales data quality pipeline.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "data-quality"],
)
def portfolio_sales_data_quality():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_sales_data_quality()

