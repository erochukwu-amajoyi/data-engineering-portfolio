from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from api_pipeline import extract_data, transform_data  # noqa: E402


class FakeResponse:
    def __init__(self, payload, status_error=None):
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def json(self):
        return self.payload


def sample_payload():
    return {
        "current_weather": {
            "temperature": 22.5,
            "windspeed": 8.2,
            "winddirection": 180,
            "time": "2025-01-10T10:00",
        }
    }


def test_extract_data_uses_requests_get(monkeypatch):
    calls = {}

    def fake_get(url, timeout):
        calls["url"] = url
        calls["timeout"] = timeout
        return FakeResponse(sample_payload())

    monkeypatch.setattr("api_pipeline.requests.get", fake_get)

    payload = extract_data(url="https://example.test/weather", timeout=3)

    assert payload == sample_payload()
    assert calls == {"url": "https://example.test/weather", "timeout": 3}


def test_transform_data_creates_single_weather_row():
    df = transform_data(sample_payload())

    assert len(df) == 1
    assert df.loc[0, "temperature"] == 22.5
    assert pd.api.types.is_datetime64_any_dtype(df["observation_time"])


def test_transform_data_rejects_missing_current_weather():
    with pytest.raises(ValueError, match="current_weather"):
        transform_data({})


def test_transform_data_rejects_missing_required_fields():
    with pytest.raises(ValueError, match="windspeed"):
        transform_data(
            {
                "current_weather": {
                    "temperature": 22.5,
                    "winddirection": 180,
                    "time": "2025-01-10T10:00",
                }
            }
        )

