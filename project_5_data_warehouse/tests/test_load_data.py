from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from load_data import build_warehouse_tables, transform_source_data, validate_columns  # noqa: E402


def sample_sales():
    return pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_name": "Alice",
                "product": "Laptop",
                "category": "Electronics",
                "amount": "1200",
                "order_date": "2025-01-10",
            },
            {
                "order_id": 2,
                "customer_name": "Bob",
                "product": "Phone",
                "category": "Electronics",
                "amount": "800",
                "order_date": "2025-01-11",
            },
            {
                "order_id": 3,
                "customer_name": "Alice",
                "product": "Mouse",
                "category": "Accessories",
                "amount": "25",
                "order_date": "2025-01-12",
            },
        ]
    )


def test_validate_columns_rejects_missing_columns():
    with pytest.raises(ValueError, match="category"):
        validate_columns(pd.DataFrame({"order_id": [1]}))


def test_transform_source_data_converts_types():
    transformed = transform_source_data(sample_sales())

    assert pd.api.types.is_datetime64_any_dtype(transformed["order_date"])
    assert pd.api.types.is_numeric_dtype(transformed["amount"])


def test_build_warehouse_tables_creates_dimensions_and_fact():
    tables = build_warehouse_tables(transform_source_data(sample_sales()))

    assert set(tables) == {"dim_customer", "dim_product", "dim_date", "fact_sales"}
    assert len(tables["dim_customer"]) == 2
    assert len(tables["dim_product"]) == 3
    assert len(tables["dim_date"]) == 3
    assert len(tables["fact_sales"]) == 3
    assert set(tables["fact_sales"].columns) == {
        "order_id",
        "customer_key",
        "product_key",
        "date_key",
        "amount",
    }

