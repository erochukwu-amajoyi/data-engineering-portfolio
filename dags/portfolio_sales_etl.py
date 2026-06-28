from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_1_csv_pipeline")
from etl_pipeline import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_sales_batch_etl",
    description="Run the batch sales CSV ETL pipeline.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "sales", "etl"],
)
def portfolio_sales_batch_etl():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_sales_batch_etl()

