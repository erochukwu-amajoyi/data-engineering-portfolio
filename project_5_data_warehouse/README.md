# Dimensional Data Warehouse

This project converts flat sales data into a small star schema. It demonstrates warehouse modeling fundamentals: dimensions, facts, surrogate keys, and SQL schema management.

## What It Demonstrates

- Star schema design.
- Customer, product, and date dimensions.
- Sales fact table generation.
- Surrogate key assignment.
- SQL DDL for warehouse tables.
- Repeatable local loading into Postgres.
- Unit tests for dimensional transforms.
- Airflow scheduling with retries.

## Warehouse Tables

| Table | Grain |
| --- | --- |
| `dim_customer` | One row per customer |
| `dim_product` | One row per product/category pair |
| `dim_date` | One row per order date |
| `fact_sales` | One row per source order |

## Run Locally

Preview generated warehouse tables:

```bash
python project_5_data_warehouse/scripts/load_data.py --dry-run
```

Load to Postgres:

```bash
python project_5_data_warehouse/scripts/load_data.py
```

Run tests:

```bash
python -m pytest project_5_data_warehouse/tests -q
```

## Configuration

| Variable | Default |
| --- | --- |
| `WAREHOUSE_INPUT_PATH` | `project_5_data_warehouse/data/sales_data.csv` |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/data_projects` |

