# Nested JSON Order Normalization

This project converts nested order JSON into normalized relational tables. It is designed to demonstrate the common data engineering task of turning semi-structured source data into warehouse-ready tables.

## What It Demonstrates

- JSON extraction.
- Payload shape validation.
- Nested array normalization.
- Order-level and item-level table generation.
- Type conversion for dates and prices.
- Environment-based database configuration.
- Unit tests for transform logic.
- Airflow scheduling with retries.

## Output Tables

`orders`

| Column | Description |
| --- | --- |
| `order_id` | Source order identifier |
| `customer_name` | Customer name |
| `order_date` | Parsed order date |
| `item_count` | Number of items in the order |
| `order_total` | Sum of item prices |

`order_items`

| Column | Description |
| --- | --- |
| `order_id` | Parent order identifier |
| `line_number` | Item position within the order |
| `product` | Product name |
| `price` | Item price |

## Run Locally

Preview normalized tables:

```bash
python project_4_json_pipeline/scripts/json_pipeline.py --dry-run
```

Load to Postgres:

```bash
python project_4_json_pipeline/scripts/json_pipeline.py
```

Run tests:

```bash
python -m pytest project_4_json_pipeline/tests -q
```

## Configuration

| Variable | Default |
| --- | --- |
| `JSON_ORDERS_INPUT_PATH` | `project_4_json_pipeline/data/orders.json` |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/data_projects` |
| `JSON_ORDERS_TABLE_NAME` | `orders` |
| `JSON_ORDER_ITEMS_TABLE_NAME` | `order_items` |
| `JSON_LOAD_MODE` | `replace` |

