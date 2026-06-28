from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from ecommerce_pipeline import run_pipeline  # noqa: E402


DEFAULT_ARGS = {
    "owner": "data-engineering-portfolio",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="ecommerce_analytics",
    description="Build e-commerce revenue, product, and customer analytics marts.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["portfolio", "ecommerce", "analytics"],
)
def ecommerce_analytics():
    @task()
    def run_ecommerce_pipeline():
        run_pipeline()

    run_ecommerce_pipeline()


ecommerce_analytics()

