from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from load_data import run_pipeline  # noqa: E402


DEFAULT_ARGS = {
    "owner": "data-engineering-portfolio",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="sales_dimensional_warehouse_load",
    description="Build and load customer, product, date, and sales fact tables.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["portfolio", "warehouse", "star-schema"],
)
def sales_dimensional_warehouse_load():
    @task()
    def run_warehouse_load():
        run_pipeline()

    run_warehouse_load()


sales_dimensional_warehouse_load()

