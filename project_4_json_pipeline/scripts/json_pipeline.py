import argparse
import json
import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
REQUIRED_ORDER_FIELDS = {"order_id", "customer_name", "order_date", "items"}
REQUIRED_ITEM_FIELDS = {"product", "price"}
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
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    logger.info("Extracted %s orders from %s", len(data) if isinstance(data, list) else 0, input_path)
    return data


def validate_order(order, index):
    missing_fields = sorted(REQUIRED_ORDER_FIELDS - set(order))
    if missing_fields:
        raise ValueError(f"Order at index {index} is missing fields: {', '.join(missing_fields)}")
    if not isinstance(order["items"], list) or not order["items"]:
        raise ValueError(f"Order {order['order_id']} must contain a non-empty items list")


def validate_item(item, order_id, line_number):
    missing_fields = sorted(REQUIRED_ITEM_FIELDS - set(item))
    if missing_fields:
        raise ValueError(
            f"Order {order_id} item {line_number} is missing fields: {', '.join(missing_fields)}"
        )


def transform_data(data):
    if not isinstance(data, list):
        raise ValueError("Expected JSON payload to be a list of orders")

    orders = []
    items = []

    for index, order in enumerate(data):
        validate_order(order, index)
        order_date = pd.to_datetime(order["order_date"], errors="raise")
        order_items = []

        for line_number, item in enumerate(order["items"], start=1):
            validate_item(item, order["order_id"], line_number)
            price = pd.to_numeric(item["price"], errors="raise")
            if price < 0:
                raise ValueError(f"Order {order['order_id']} item {line_number} has a negative price")

            normalized_item = {
                "order_id": order["order_id"],
                "line_number": line_number,
                "product": str(item["product"]).strip(),
                "price": price,
            }
            order_items.append(normalized_item)
            items.append(normalized_item)

        orders.append(
            {
                "order_id": order["order_id"],
                "customer_name": str(order["customer_name"]).strip(),
                "order_date": order_date,
                "item_count": len(order_items),
                "order_total": sum(item["price"] for item in order_items),
            }
        )

    orders_df = pd.DataFrame(orders)
    items_df = pd.DataFrame(items)
    logger.info("Normalized %s orders and %s items", len(orders_df), len(items_df))
    return orders_df, items_df


def load_data(orders_df, items_df, database_url=None, orders_table=None, items_table=None, if_exists=None):
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/data_projects",
    )
    orders_table = orders_table or os.getenv("JSON_ORDERS_TABLE_NAME", "orders")
    items_table = items_table or os.getenv("JSON_ORDER_ITEMS_TABLE_NAME", "order_items")
    if_exists = if_exists or os.getenv("JSON_LOAD_MODE", "replace")

    engine = create_engine(database_url)
    orders_df.to_sql(orders_table, engine, if_exists=if_exists, index=False)
    items_df.to_sql(items_table, engine, if_exists=if_exists, index=False)
    logger.info("Loaded %s orders into %s", len(orders_df), orders_table)
    logger.info("Loaded %s order items into %s", len(items_df), items_table)


def run_pipeline(input_path=None, dry_run=False):
    configure_logging()
    input_path = input_path or os.getenv(
        "JSON_ORDERS_INPUT_PATH",
        "project_4_json_pipeline/data/orders.json",
    )

    data = extract_data(input_path)
    orders_df, items_df = transform_data(data)

    if dry_run:
        print("Orders:")
        print(orders_df.to_string(index=False))
        print("\nOrder items:")
        print(items_df.to_string(index=False))
        logger.info("Dry run completed successfully")
        return orders_df, items_df

    load_data(orders_df, items_df)
    logger.info("JSON normalization pipeline executed successfully")
    return orders_df, items_df


def parse_args():
    parser = argparse.ArgumentParser(description="Normalize nested JSON order data.")
    parser.add_argument("--input-path", default=None, help="JSON input path.")
    parser.add_argument("--dry-run", action="store_true", help="Print normalized tables without loading.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(input_path=args.input_path, dry_run=args.dry_run)
