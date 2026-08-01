# Retail Analytics Engineering with dbt

This project models raw retail data into tested analytics marts using a dbt-compatible project structure. It is designed for analytics engineering roles where SQL modelling, documentation, data quality tests, and business metrics matter as much as ingestion.

No cloud account is required. The project can be validated locally with the included Python/SQLite runner, and the dbt files are ready to run with `dbt-duckdb` if installed.

## What It Demonstrates

- Raw-to-staging-to-mart modelling.
- SQL transformations using dbt `ref()` dependencies.
- Fact and dimension tables for reporting.
- Customer lifetime value and daily revenue marts.
- Generic dbt tests such as `not_null`, `unique`, and accepted values.
- Singular data tests for revenue quality and reconciliation.
- Documentation-ready model and column descriptions.
- Optional Snowflake profile template using environment variables only.

## Analytics Marts

| Model | Purpose |
| --- | --- |
| `fct_orders` | Order-level revenue facts for financial reporting |
| `dim_customers` | Customer attributes plus first order, latest order, and repeat-customer flags |
| `dim_products` | Product catalogue with units sold and revenue metrics |
| `mart_daily_revenue` | Daily revenue, order count, units sold, and average order value |
| `mart_customer_lifetime_value` | Customer value bands and average order value for segmentation |

## Run Locally

Validate the project without installing dbt:

```bash
python project_9_analytics_engineering/scripts/build_local_analytics.py --dry-run
```

Run the tests:

```bash
python -m pytest project_9_analytics_engineering/tests -q
```

## Optional dbt Run

If `dbt-core` and `dbt-duckdb` are installed, the same models can run through dbt:

```bash
cd project_9_analytics_engineering
dbt seed --profiles-dir .
dbt build --profiles-dir .
dbt docs generate --profiles-dir .
```

The included `profiles.yml` uses a local DuckDB file under `target/`. `profiles_snowflake.yml.example` shows how the project would be pointed at Snowflake with environment variables instead of hard-coded credentials.

## Repository Evidence

| Area | Files |
| --- | --- |
| dbt configuration | `dbt_project.yml`, `profiles.yml`, `profiles_snowflake.yml.example` |
| Raw data | `seeds/raw_orders.csv`, `seeds/raw_customers.csv`, `seeds/raw_products.csv` |
| SQL models | `models/staging/`, `models/intermediate/`, `models/marts/` |
| Data tests | `models/**/schema.yml`, `tests/*.sql` |
| Local validation | `scripts/build_local_analytics.py`, `tests/test_analytics_build.py` |
| BI-ready queries | `analyses/revenue_dashboard_queries.sql` |
