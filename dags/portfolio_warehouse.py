from datetime import datetime, timedelta

from airflow.decorators import dag, task

from _portfolio import add_project_scripts


add_project_scripts("project_5_data_warehouse")
from load_data import run_pipeline  # noqa: E402


@dag(
    dag_id="portfolio_dimensional_warehouse",
    description="Build and load dimensional warehouse tables.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "warehouse"],
)
def portfolio_dimensional_warehouse():
    @task()
    def run():
        run_pipeline()

    run()


portfolio_dimensional_warehouse()

