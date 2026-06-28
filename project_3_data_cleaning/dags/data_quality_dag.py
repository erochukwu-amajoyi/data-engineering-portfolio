from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from cleaning_pipeline import run_pipeline  # noqa: E402


DEFAULT_ARGS = {
    "owner": "data-engineering-portfolio",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="sales_data_quality",
    description="Validate raw sales data and write clean and rejected records.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["portfolio", "data-quality", "sales"],
)
def sales_data_quality():
    @task()
    def run_quality_pipeline():
        run_pipeline()

    run_quality_pipeline()


sales_data_quality()

