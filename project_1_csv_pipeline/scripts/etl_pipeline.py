import argparse
import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
REQUIRED_COLUMNS = {"order_id", "customer_name", "product", "amount", "order_date"}
logger = logging.getLogger(__name__)


def configure_logging():
    if logging.getLogger().handlers:
        return

    log_dir = PROJECT_ROOT / "logs"
    try:
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "pipeline.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    except OSError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logger.warning("File logging unavailable; using console logging instead")


def resolve_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path

    repo_candidate = REPO_ROOT / path
    if repo_candidate.exists():
        return repo_candidate

    return PROJECT_ROOT / path


def extract_data(file_path):
    input_path = resolve_path(file_path)
    df = pd.read_csv(input_path)
    logger.info("Extracted %s rows from %s", len(df), input_path)
    return df


def validate_columns(df):
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")


def transform_data(df):
    validate_columns(df)

    transformed = df.copy()
    transformed = transformed.drop_duplicates().reset_index(drop=True)
    transformed["amount"] = pd.to_numeric(transformed["amount"], errors="coerce").fillna(0)
    transformed["order_date"] = pd.to_datetime(transformed["order_date"], errors="raise")

    logger.info("Transformed %s rows", len(transformed))
    return transformed


def load_data(df, database_url=None, table_name=None, if_exists=None):
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/data_projects",
    )
    table_name = table_name or os.getenv("SALES_TABLE_NAME", "sales")
    if_exists = if_exists or os.getenv("SALES_LOAD_MODE", "replace")

    engine = create_engine(database_url)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.info("Loaded %s rows into table %s", len(df), table_name)


def run_pipeline(input_path=None, dry_run=False):
    configure_logging()
    input_path = input_path or os.getenv(
        "SALES_INPUT_PATH",
        "project_1_csv_pipeline/data/sales_data.csv",
    )

    df = extract_data(input_path)
    transformed = transform_data(df)

    if dry_run:
        print(transformed.to_string(index=False))
        logger.info("Dry run completed successfully")
        return transformed

    load_data(transformed)
    logger.info("Pipeline executed successfully")
    return transformed


def parse_args():
    parser = argparse.ArgumentParser(description="Run the batch sales ETL pipeline.")
    parser.add_argument(
        "--input-path",
        default=None,
        help="CSV input path. Defaults to SALES_INPUT_PATH or bundled sample data.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print transformed data without loading it to Postgres.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(input_path=args.input_path, dry_run=args.dry_run)
