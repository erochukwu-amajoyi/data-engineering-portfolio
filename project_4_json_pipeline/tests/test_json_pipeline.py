from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from json_pipeline import extract_data, transform_data  # noqa: E402


def sample_orders():
    return [
        {
            "order_id": 1,
            "customer_name": "Alice",
            "order_date": "2025-01-10",
            "items": [
                {"product": "Laptop", "price": 1200},
                {"product": "Mouse", "price": 25},
            ],
        },
        {
            "order_id": 2,
            "customer_name": "Bob",
            "order_date": "2025-01-11",
            "items": [{"product": "Phone", "price": 800}],
        },
    ]


def test_extract_data_reads_json_file():
    data = extract_data(PROJECT_ROOT / "data" / "orders.json")

    assert len(data) == 2
    assert data[0]["order_id"] == 1


def test_transform_data_normalizes_orders_and_items():
    orders_df, items_df = transform_data(sample_orders())

    assert orders_df["order_id"].tolist() == [1, 2]
    assert orders_df.loc[0, "item_count"] == 2
    assert orders_df.loc[0, "order_total"] == 1225
    assert items_df["line_number"].tolist() == [1, 2, 1]
    assert pd.api.types.is_datetime64_any_dtype(orders_df["order_date"])


def test_transform_data_rejects_non_list_payload():
    with pytest.raises(ValueError, match="list of orders"):
        transform_data({"order_id": 1})


def test_transform_data_rejects_missing_order_fields():
    with pytest.raises(ValueError, match="customer_name"):
        transform_data([{"order_id": 1, "order_date": "2025-01-10", "items": []}])


def test_transform_data_rejects_missing_item_fields():
    with pytest.raises(ValueError, match="price"):
        transform_data(
            [
                {
                    "order_id": 1,
                    "customer_name": "Alice",
                    "order_date": "2025-01-10",
                    "items": [{"product": "Laptop"}],
                }
            ]
        )

