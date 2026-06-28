# Log Analytics and Incremental Processing Pipeline

This project parses application logs into structured records, builds log analytics marts, and supports incremental processing through a local state file.

## What It Demonstrates

- Regex-based log parsing.
- Rejected-line capture for malformed logs.
- Timestamp conversion and structured fields.
- Incremental processing with a saved high-watermark timestamp.
- Log-level, user, and product-event analytics.
- Environment-based database configuration.
- Unit tests for parsing, analytics, and incremental filtering.
- Airflow scheduling with retries.

## Output Tables

| Table | Purpose |
| --- | --- |
| `parsed_logs` | Structured log events |
| `log_level_counts` | Event counts by log level |
| `user_activity` | Event counts and first/last activity by user |
| `product_events` | Event counts by product |

## Run Locally

Preview parsed logs and analytics without writing state:

```bash
python project_7_log_pipeline/scripts/log_pipeline.py --dry-run --no-state
```

Run with incremental state and load to Postgres:

```bash
python project_7_log_pipeline/scripts/log_pipeline.py
```

Run tests:

```bash
python -m pytest project_7_log_pipeline/tests -q
```

## Configuration

| Variable | Default |
| --- | --- |
| `LOG_INPUT_PATH` | `project_7_log_pipeline/data/app.log` |
| `LOG_STATE_PATH` | `project_7_log_pipeline/state/log_state.json` |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/data_projects` |

