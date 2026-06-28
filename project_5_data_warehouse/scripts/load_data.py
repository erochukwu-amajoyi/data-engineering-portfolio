import argparse
import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
REQUIRED_COLUMNS = {"order_id", "customer_name", "product", "category", "amount", "order_date"}
logger = logging.getLogger(__name__)


def configure_logging():
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def resolve_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path

    repo_candidate = REPO_ROOT / path
    if repo_candidate.exists():
        return repo_candidate

    return PROJECT_ROOT / path


def validate_columns(df):
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")


def extract_data(file_path):
    input_path = resolve_path(file_path)
    df = pd.read_csv(input_path)
    logger.info("Extracted %s source rows from %s", len(df), input_path)
    return df


def transform_source_data(df):
    validate_columns(df)

    transformed = df.copy().drop_duplicates().reset_index(drop=True)
    transformed["customer_name"] = transformed["customer_name"].astype(str).str.strip()
    transformed["product"] = transformed["product"].astype(str).str.strip()
    transformed["category"] = transformed["category"].astype(str).str.strip()
    transformed["amount"] = pd.to_numeric(transformed["amount"], errors="raise")
    transformed["order_date"] = pd.to_datetime(transformed["order_date"], errors="raise")
    return transformed


def assign_keys(df, key_name):
    keyed = df.copy().reset_index(drop=True)
    keyed.insert(0, key_name, range(1, len(keyed) + 1))
    return keyed


def build_warehouse_tables(df):
    dim_customer = assign_keys(
        df[["customer_name"]].drop_duplicates().sort_values("customer_name"),
        "customer_key",
    )

    dim_product = assign_keys(
        df[["product", "category"]].drop_duplicates().sort_values(["category", "product"]),
        "product_key",
    )

    dim_date = df[["order_date"]].drop_duplicates().sort_values("order_date")
    dim_date = dim_date.assign(
        date_key=dim_date["order_date"].dt.strftime("%Y%m%d").astype(int),
        full_date=dim_date["order_date"].dt.date,
        year=dim_date["order_date"].dt.year,
        month=dim_date["order_date"].dt.month,
        day=dim_date["order_date"].dt.day,
    )[["date_key", "full_date", "year", "month", "day"]]

    fact_sales = (
        df.merge(dim_customer, on="customer_name", how="left")
        .merge(dim_product, on=["product", "category"], how="left")
        .assign(date_key=lambda merged: merged["order_date"].dt.strftime("%Y%m%d").astype(int))
        [["order_id", "customer_key", "product_key", "date_key", "amount"]]
    )

    tables = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_date": dim_date,
        "fact_sales": fact_sales,
    }
    logger.info("Built warehouse tables: %s", ", ".join(tables))
    return tables


def load_warehouse(tables, database_url=None):
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/data_projects",
    )
    schema_sql = (PROJECT_ROOT / "sql" / "schema.sql").read_text()
    engine = create_engine(database_url)

    with engine.begin() as connection:
        connection.execute(text(schema_sql))
        connection.execute(
            text(
                "TRUNCATE TABLE fact_sales, dim_date, dim_product, dim_customer "
                "RESTART IDENTITY CASCADE"
            )
        )

    for table_name in ["dim_customer", "dim_product", "dim_date", "fact_sales"]:
        tables[table_name].to_sql(table_name, engine, if_exists="append", index=False)
        logger.info("Loaded %s rows into %s", len(tables[table_name]), table_name)


def run_pipeline(input_path=None, dry_run=False):
    configure_logging()
    input_path = input_path or os.getenv(
        "WAREHOUSE_INPUT_PATH",
        "project_5_data_warehouse/data/sales_data.csv",
    )

    raw_df = extract_data(input_path)
    transformed_df = transform_source_data(raw_df)
    tables = build_warehouse_tables(transformed_df)

    if dry_run:
        for table_name, table_df in tables.items():
            print(f"\n{table_name}:")
            print(table_df.to_string(index=False))
        return tables

    load_warehouse(tables)
    logger.info("Dimensional warehouse load completed successfully")
    return tables


def parse_args():
    parser = argparse.ArgumentParser(description="Build and load a dimensional sales warehouse.")
    parser.add_argument("--input-path", default=None, help="Source sales CSV path.")
    parser.add_argument("--dry-run", action="store_true", help="Print warehouse tables without loading.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(input_path=args.input_path, dry_run=args.dry_run)
