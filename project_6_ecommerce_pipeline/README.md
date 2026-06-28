# E-commerce Analytics Pipeline

This project joins orders, customers, and products into analytics-ready tables for revenue and customer behavior analysis.

## What It Demonstrates

- Multi-source CSV ingestion.
- Referential checks across orders, customers, and products.
- Revenue calculation.
- Analytics marts for daily revenue, top products, and customer metrics.
- Repeat-customer identification.
- Environment-based database configuration.
- Unit tests for joins and KPI logic.
- Airflow scheduling with retries.

## Output Tables

| Table | Purpose |
| --- | --- |
| `ecommerce_orders` | Enriched order-level records |
| `daily_revenue` | Revenue and order counts by date |
| `top_products` | Product revenue and units sold |
| `customer_metrics` | Customer-level order count, revenue, and repeat-customer flag |

## Run Locally

Preview analytics tables:

```bash
python project_6_ecommerce_pipeline/scripts/ecommerce_pipeline.py --dry-run
```

Load to Postgres:

```bash
python project_6_ecommerce_pipeline/scripts/ecommerce_pipeline.py
```

Run tests:

```bash
python -m pytest project_6_ecommerce_pipeline/tests -q
```

## Configuration

| Variable | Default |
| --- | --- |
| `ECOMMERCE_ORDERS_PATH` | `project_6_ecommerce_pipeline/data/orders.csv` |
| `ECOMMERCE_CUSTOMERS_PATH` | `project_6_ecommerce_pipeline/data/customers.csv` |
| `ECOMMERCE_PRODUCTS_PATH` | `project_6_ecommerce_pipeline/data/products.csv` |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/data_projects` |

