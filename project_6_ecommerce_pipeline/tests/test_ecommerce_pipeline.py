from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from ecommerce_pipeline import generate_analytics, transform_data  # noqa: E402


def sample_sources():
    orders = pd.DataFrame(
        [
            {"order_id": 1, "customer_id": 101, "product_id": 1001, "quantity": 1, "order_date": "2025-01-10"},
            {"order_id": 2, "customer_id": 102, "product_id": 1002, "quantity": 2, "order_date": "2025-01-11"},
            {"order_id": 3, "customer_id": 101, "product_id": 1003, "quantity": 1, "order_date": "2025-01-12"},
        ]
    )
    customers = pd.DataFrame(
        [
            {"customer_id": 101, "customer_name": "Alice"},
            {"customer_id": 102, "customer_name": "Bob"},
        ]
    )
    products = pd.DataFrame(
        [
            {"product_id": 1001, "product_name": "Laptop", "price": 1200},
            {"product_id": 1002, "product_name": "Phone", "price": 800},
            {"product_id": 1003, "product_name": "Mouse", "price": 25},
        ]
    )
    return orders, customers, products


def test_transform_data_joins_sources_and_calculates_revenue():
    orders, customers, products = sample_sources()
    enriched = transform_data(orders, customers, products)

    assert len(enriched) == 3
    assert enriched.loc[1, "revenue"] == 1600
    assert pd.api.types.is_datetime64_any_dtype(enriched["order_date"])


def test_transform_data_rejects_unknown_customer():
    orders, customers, products = sample_sources()
    orders.loc[0, "customer_id"] = 999

    with pytest.raises(ValueError, match="unknown customer_id"):
        transform_data(orders, customers, products)


def test_generate_analytics_builds_expected_marts():
    orders, customers, products = sample_sources()
    enriched = transform_data(orders, customers, products)
    marts = generate_analytics(enriched)

    assert set(marts) == {
        "ecommerce_orders",
        "daily_revenue",
        "top_products",
        "customer_metrics",
    }
    assert marts["top_products"].iloc[0]["product_name"] == "Phone"
    alice = marts["customer_metrics"][marts["customer_metrics"]["customer_name"] == "Alice"].iloc[0]
    assert alice["repeat_customer"] is True

