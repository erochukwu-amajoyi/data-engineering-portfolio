import argparse
import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
logger = logging.getLogger(__name__)

ORDER_COLUMNS = {"order_id", "customer_id", "product_id", "quantity", "order_date"}
CUSTOMER_COLUMNS = {"customer_id", "customer_name"}
PRODUCT_COLUMNS = {"product_id", "product_name", "price"}


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


def validate_columns(df, required_columns, dataset_name):
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"{dataset_name} is missing required columns: {', '.join(missing_columns)}")


def extract_data(orders_path=None, customers_path=None, products_path=None):
    orders_path = resolve_path(
        orders_path or os.getenv("ECOMMERCE_ORDERS_PATH", "project_6_ecommerce_pipeline/data/orders.csv")
    )
    customers_path = resolve_path(
        customers_path or os.getenv("ECOMMERCE_CUSTOMERS_PATH", "project_6_ecommerce_pipeline/data/customers.csv")
    )
    products_path = resolve_path(
        products_path or os.getenv("ECOMMERCE_PRODUCTS_PATH", "project_6_ecommerce_pipeline/data/products.csv")
    )

    orders = pd.read_csv(orders_path)
    customers = pd.read_csv(customers_path)
    products = pd.read_csv(products_path)
    logger.info("Extracted %s orders, %s customers, %s products", len(orders), len(customers), len(products))
    return orders, customers, products


def validate_references(orders, customers, products):
    unknown_customers = sorted(set(orders["customer_id"]) - set(customers["customer_id"]))
    if unknown_customers:
        raise ValueError(f"Orders reference unknown customer_id values: {unknown_customers}")

    unknown_products = sorted(set(orders["product_id"]) - set(products["product_id"]))
    if unknown_products:
        raise ValueError(f"Orders reference unknown product_id values: {unknown_products}")


def transform_data(orders, customers, products):
    validate_columns(orders, ORDER_COLUMNS, "orders")
    validate_columns(customers, CUSTOMER_COLUMNS, "customers")
    validate_columns(products, PRODUCT_COLUMNS, "products")
    validate_references(orders, customers, products)

    orders = orders.copy()
    products = products.copy()
    orders["quantity"] = pd.to_numeric(orders["quantity"], errors="raise")
    products["price"] = pd.to_numeric(products["price"], errors="raise")
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="raise")

    if (orders["quantity"] <= 0).any():
        raise ValueError("Orders contain non-positive quantity values")
    if (products["price"] < 0).any():
        raise ValueError("Products contain negative price values")

    enriched = orders.merge(customers, on="customer_id", how="left").merge(products, on="product_id", how="left")
    enriched["revenue"] = enriched["quantity"] * enriched["price"]

    columns = [
        "order_id",
        "order_date",
        "customer_id",
        "customer_name",
        "product_id",
        "product_name",
        "quantity",
        "price",
        "revenue",
    ]
    logger.info("Built enriched e-commerce dataset with %s rows", len(enriched))
    return enriched[columns]


def generate_analytics(enriched):
    ecommerce_orders = enriched.sort_values("order_id").reset_index(drop=True)

    daily_revenue = (
        ecommerce_orders.assign(order_date=ecommerce_orders["order_date"].dt.date)
        .groupby("order_date", as_index=False)
        .agg(order_count=("order_id", "nunique"), revenue=("revenue", "sum"))
        .sort_values("order_date")
        .reset_index(drop=True)
    )

    top_products = (
        ecommerce_orders.groupby(["product_id", "product_name"], as_index=False)
        .agg(units_sold=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values(["revenue", "units_sold"], ascending=[False, False])
        .reset_index(drop=True)
    )

    customer_metrics = (
        ecommerce_orders.groupby(["customer_id", "customer_name"], as_index=False)
        .agg(order_count=("order_id", "nunique"), total_revenue=("revenue", "sum"))
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )
    customer_metrics["repeat_customer"] = (customer_metrics["order_count"] > 1).map(lambda value: bool(value)).astype(object)

    marts = {
        "ecommerce_orders": ecommerce_orders,
        "daily_revenue": daily_revenue,
        "top_products": top_products,
        "customer_metrics": customer_metrics,
    }
    logger.info("Generated analytics marts: %s", ", ".join(marts))
    return marts


def load_data(marts, database_url=None):
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/data_projects",
    )
    engine = create_engine(database_url)

    for table_name, df in marts.items():
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        logger.info("Loaded %s rows into %s", len(df), table_name)


def run_pipeline(dry_run=False):
    configure_logging()
    orders, customers, products = extract_data()
    enriched = transform_data(orders, customers, products)
    marts = generate_analytics(enriched)

    if dry_run:
        for table_name, df in marts.items():
            print(f"\n{table_name}:")
            print(df.to_string(index=False))
        return marts

    load_data(marts)
    logger.info("E-commerce analytics pipeline completed successfully")
    return marts


def parse_args():
    parser = argparse.ArgumentParser(description="Build e-commerce analytics marts.")
    parser.add_argument("--dry-run", action="store_true", help="Print analytics tables without loading.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(dry_run=args.dry_run)
