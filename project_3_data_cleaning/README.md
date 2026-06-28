# Data Cleaning and Quality Pipeline

This project validates raw sales records, separates clean records from rejected records, and writes both outputs for auditability.

## What It Demonstrates

- Required-column validation.
- Deduplication and type standardization.
- Missing customer-name handling.
- Invalid-record quarantine with rejection reasons.
- Clean and rejected output datasets.
- Unit tests for data quality rules.
- Airflow scheduling with retries.

## Data Quality Rules

Records are rejected when they contain:

- Missing `order_id`.
- Missing `product`.
- Missing or non-numeric `amount`.
- Negative `amount`.
- Invalid `order_date`.

Missing `customer_name` values are allowed and standardized to `Unknown`.

## Architecture

```text
data/raw_data.csv
      |
      v
extract_data()
      |
      v
clean_data()
      |
      v
split_valid_rejected()
      |
      +--> data/clean_data.csv
      |
      +--> data/rejected_records.csv
```

## Run Locally

From the repository root:

```bash
python project_3_data_cleaning/scripts/cleaning_pipeline.py --dry-run
```

Write clean and rejected outputs:

```bash
python project_3_data_cleaning/scripts/cleaning_pipeline.py
```

Run tests:

```bash
python -m pytest project_3_data_cleaning/tests -q
```

## Configuration

| Variable | Default |
| --- | --- |
| `DATA_QUALITY_INPUT_PATH` | `project_3_data_cleaning/data/raw_data.csv` |
| `DATA_QUALITY_CLEAN_OUTPUT_PATH` | `project_3_data_cleaning/data/clean_data.csv` |
| `DATA_QUALITY_REJECTED_OUTPUT_PATH` | `project_3_data_cleaning/data/rejected_records.csv` |

