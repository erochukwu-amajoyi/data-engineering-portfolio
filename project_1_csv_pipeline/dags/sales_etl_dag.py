from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from etl_pipeline import run_pipeline  # noqa: E402


DEFAULT_ARGS = {
    "owner": "data-engineering-portfolio",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="sales_batch_etl",
    description="Ingest, transform, and load sales CSV data into Postgres.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["portfolio", "sales", "etl"],
)
def sales_batch_etl():
    @task()
    def run_sales_pipeline():
        run_pipeline()

    run_sales_pipeline()


sales_batch_etl()

