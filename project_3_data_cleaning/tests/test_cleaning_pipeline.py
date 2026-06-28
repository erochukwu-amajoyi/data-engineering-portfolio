from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from cleaning_pipeline import (  # noqa: E402
    clean_data,
    run_pipeline,
    split_valid_rejected,
    validate_columns,
)


def sample_raw_data():
    return pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_name": "Alice",
                "product": "Laptop",
                "amount": "1200",
                "order_date": "2025-01-10",
            },
            {
                "order_id": 2,
                "customer_name": "Bob",
                "product": "Phone",
                "amount": "-800",
                "order_date": "2025-01-11",
            },
            {
                "order_id": 3,
                "customer_name": "Charlie",
                "product": "Tablet",
                "amount": None,
                "order_date": "2025-01-32",
            },
            {
                "order_id": 4,
                "customer_name": None,
                "product": "Monitor",
                "amount": "300",
                "order_date": "2025-01-13",
            },
        ]
    )


def test_validate_columns_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_columns(pd.DataFrame({"order_id": [1]}))


def test_clean_data_standardizes_types_and_customer_names():
    cleaned = clean_data(sample_raw_data())

    assert cleaned.loc[3, "customer_name"] == "Unknown"
    assert pd.api.types.is_numeric_dtype(cleaned["amount"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned["order_date"])


def test_split_valid_rejected_keeps_bad_records_with_reasons():
    cleaned = clean_data(sample_raw_data())
    valid, rejected = split_valid_rejected(cleaned)

    assert valid["order_id"].tolist() == [1, 4]
    assert set(rejected["order_id"].tolist()) == {2, 3}
    assert "negative_amount" in rejected["rejection_reason"].tolist()
    assert any("invalid_order_date" in reason for reason in rejected["rejection_reason"])


def test_run_pipeline_writes_clean_and_rejected_outputs(tmp_path):
    input_path = tmp_path / "raw.csv"
    clean_output_path = tmp_path / "clean.csv"
    rejected_output_path = tmp_path / "rejected.csv"
    sample_raw_data().to_csv(input_path, index=False)

    valid, rejected = run_pipeline(
        input_path=input_path,
        clean_output_path=clean_output_path,
        rejected_output_path=rejected_output_path,
    )

    assert len(valid) == 2
    assert len(rejected) == 2
    assert clean_output_path.exists()
    assert rejected_output_path.exists()

