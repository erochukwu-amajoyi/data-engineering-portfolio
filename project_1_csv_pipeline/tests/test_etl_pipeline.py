from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from etl_pipeline import extract_data, transform_data  # noqa: E402


def test_extract_data_reads_csv():
    df = extract_data(PROJECT_ROOT / "data" / "sales_data.csv")

    assert list(df.columns) == [
        "order_id",
        "customer_name",
        "product",
        "amount",
        "order_date",
    ]
    assert len(df) == 5


def test_transform_data_removes_duplicates_and_fills_amounts():
    raw = pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_name": "Alice",
                "product": "Laptop",
                "amount": None,
                "order_date": "2025-01-10",
            },
            {
                "order_id": 1,
                "customer_name": "Alice",
                "product": "Laptop",
                "amount": None,
                "order_date": "2025-01-10",
            },
        ]
    )

    transformed = transform_data(raw)

    assert len(transformed) == 1
    assert transformed.loc[0, "amount"] == 0
    assert pd.api.types.is_datetime64_any_dtype(transformed["order_date"])


def test_transform_data_rejects_missing_required_columns():
    raw = pd.DataFrame({"order_id": [1]})

    with pytest.raises(ValueError, match="Missing required columns"):
        transform_data(raw)

