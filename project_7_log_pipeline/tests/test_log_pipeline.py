from pathlib import Path
import json
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from log_pipeline import (  # noqa: E402
    filter_incremental_logs,
    generate_analytics,
    parse_logs,
    transform_data,
)


def sample_logs():
    return [
        "2025-01-10 10:00:01 INFO User login success user_id=101",
        "2025-01-10 10:05:15 ERROR Payment failed user_id=102",
        "2025-01-10 10:10:20 INFO Order placed user_id=101",
        "2025-01-10 10:15:30 WARNING Low stock product_id=1001",
        "this line does not match",
    ]


def test_parse_logs_extracts_structured_fields_and_rejects_bad_lines():
    parsed, rejected = parse_logs(sample_logs())

    assert len(parsed) == 4
    assert len(rejected) == 1
    assert parsed.loc[0, "user_id"] == 101
    assert parsed.loc[3, "product_id"] == 1001
    assert rejected.loc[0, "rejection_reason"] == "unparseable_log_line"


def test_transform_data_converts_log_time():
    parsed, _ = parse_logs(sample_logs())
    transformed = transform_data(parsed)

    assert pd.api.types.is_datetime64_any_dtype(transformed["log_time"])


def test_filter_incremental_logs_uses_state_file(tmp_path):
    parsed, _ = parse_logs(sample_logs())
    transformed = transform_data(parsed)
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps({"last_log_time": "2025-01-10T10:05:15"}))

    filtered = filter_incremental_logs(transformed, state_path)

    assert filtered["log_time"].min() > pd.Timestamp("2025-01-10 10:05:15")
    assert len(filtered) == 2


def test_generate_analytics_builds_expected_marts():
    parsed, _ = parse_logs(sample_logs())
    transformed = transform_data(parsed)
    marts = generate_analytics(transformed)

    assert set(marts) == {
        "parsed_logs",
        "log_level_counts",
        "user_activity",
        "product_events",
    }
    assert marts["log_level_counts"].set_index("log_level").loc["INFO", "event_count"] == 2
    assert marts["user_activity"].set_index("user_id").loc[101, "event_count"] == 2

