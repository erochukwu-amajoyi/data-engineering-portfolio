# Batch Sales ETL Platform

This project is the first reference implementation in the portfolio. It ingests raw sales CSV data, applies repeatable transformations, and loads the result into a Postgres table.

## What It Demonstrates

- CSV extraction with pandas.
- Data validation for required columns.
- Deduplication and missing-value handling.
- Date parsing and numeric type cleanup.
- Environment-based database configuration.
- Repeatable warehouse loads.
- Unit tests for transformation logic.
- Local Postgres through Docker Compose.

## Architecture

```text
data/sales_data.csv
        |
        v
extract_data()
        |
        v
transform_data()
        |
        v
Postgres table: sales
```

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start local Postgres:

```bash
cd project_1_csv_pipeline
docker compose up -d
```

Run the pipeline:

```bash
python scripts/etl_pipeline.py
```

Preview the transformed data without loading to Postgres:

```bash
python scripts/etl_pipeline.py --dry-run
```

Run tests:

```bash
python -m pytest project_1_csv_pipeline/tests -q
```

## Airflow Orchestration

The Airflow DAG lives at `dags/sales_etl_dag.py` and schedules the batch ETL daily with retries. In a full Airflow environment, copy or mount this project into the Airflow `dags` directory and make sure the same `DATABASE_URL` configuration is available to the scheduler and workers.

## Configuration

The pipeline reads these environment variables:

| Variable | Default |
| --- | --- |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/data_projects` |
| `SALES_INPUT_PATH` | `project_1_csv_pipeline/data/sales_data.csv` |
| `SALES_TABLE_NAME` | `sales` |
| `SALES_LOAD_MODE` | `replace` |

