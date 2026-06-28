from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from log_pipeline import run_pipeline  # noqa: E402


DEFAULT_ARGS = {
    "owner": "data-engineering-portfolio",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="log_analytics_incremental",
    description="Parse application logs incrementally and build log analytics marts.",
    start_date=datetime(2025, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["portfolio", "logs", "incremental"],
)
def log_analytics_incremental():
    @task()
    def run_log_pipeline():
        run_pipeline()

    run_log_pipeline()


log_analytics_incremental()

