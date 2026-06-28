# Resilient API Ingestion Pipeline

This project ingests weather data from an external API, validates the payload shape, transforms it into an analytics-ready table, and loads it into Postgres.

## What It Demonstrates

- API ingestion with timeout handling.
- HTTP error handling through `raise_for_status`.
- Environment-based API and database configuration.
- Payload validation before transformation.
- Timestamp parsing.
- Unit tests that avoid live network dependency.
- Airflow scheduling with retries.

## Architecture

```text
Weather API
    |
    v
extract_data()
    |
    v
transform_data()
    |
    v
Postgres table: weather_data
```

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run a dry run:

```bash
python project_2_api_pipeline/scripts/api_pipeline.py --dry-run
```

Run tests:

```bash
python -m pytest project_2_api_pipeline/tests -q
```

## Airflow Orchestration

The DAG lives at `dags/weather_api_dag.py` and schedules the ingestion daily with retries. In a full Airflow environment, mount this project into the Airflow `dags` directory and provide `WEATHER_API_URL` and `DATABASE_URL` to the scheduler and workers.

## Configuration

| Variable | Default |
| --- | --- |
| `WEATHER_API_URL` | Open-Meteo current-weather endpoint |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/data_projects` |
| `WEATHER_TABLE_NAME` | `weather_data` |
| `WEATHER_LOAD_MODE` | `append` |

