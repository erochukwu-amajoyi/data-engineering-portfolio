# Local Platform

This repository includes a local data platform for portfolio demos:

- Postgres for pipeline outputs and Airflow metadata.
- Airflow webserver and scheduler.
- Root-level DAG wrappers in `dags/`.
- Project source code mounted into the Airflow containers at `/opt/airflow/repo`.

## Start the Platform

```bash
make up
```

Airflow UI:

- URL: `http://localhost:8081`
- Username: `admin`
- Password: `admin`

Postgres:

- Host from your laptop: `localhost`
- Port from your laptop: `5433`
- Host from containers: `postgres`
- User: `postgres`
- Password: `postgres`
- Portfolio database: `data_projects`
- Airflow metadata database: `airflow`

## Stop the Platform

```bash
make down
```

## Useful Commands

```bash
make test
make dry-run-all
make ci
make airflow-logs
make postgres-shell
```

## DAGs

The container scans the root `dags/` folder:

- `portfolio_sales_batch_etl`
- `portfolio_weather_api_ingestion`
- `portfolio_sales_data_quality`
- `portfolio_json_order_normalization`
- `portfolio_dimensional_warehouse`
- `portfolio_ecommerce_analytics`
- `portfolio_log_analytics_incremental`

## Notes

The weather API DAG requires outbound internet access from the Airflow worker. The CI workflow avoids live API calls by using mocked unit tests.

