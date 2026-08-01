import argparse
import csv
import re
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SEEDS = {
    "raw_customers": PROJECT_ROOT / "seeds" / "raw_customers.csv",
    "raw_orders": PROJECT_ROOT / "seeds" / "raw_orders.csv",
    "raw_products": PROJECT_ROOT / "seeds" / "raw_products.csv",
}

MODEL_ORDER = [
    "stg_customers",
    "stg_products",
    "stg_orders",
    "int_order_items_enriched",
    "dim_customers",
    "dim_products",
    "fct_orders",
    "mart_customer_lifetime_value",
    "mart_daily_revenue",
]

MODEL_PATHS = {
    "stg_customers": PROJECT_ROOT / "models" / "staging" / "stg_customers.sql",
    "stg_products": PROJECT_ROOT / "models" / "staging" / "stg_products.sql",
    "stg_orders": PROJECT_ROOT / "models" / "staging" / "stg_orders.sql",
    "int_order_items_enriched": PROJECT_ROOT / "models" / "intermediate" / "int_order_items_enriched.sql",
    "dim_customers": PROJECT_ROOT / "models" / "marts" / "dim_customers.sql",
    "dim_products": PROJECT_ROOT / "models" / "marts" / "dim_products.sql",
    "fct_orders": PROJECT_ROOT / "models" / "marts" / "fct_orders.sql",
    "mart_customer_lifetime_value": PROJECT_ROOT / "models" / "marts" / "mart_customer_lifetime_value.sql",
    "mart_daily_revenue": PROJECT_ROOT / "models" / "marts" / "mart_daily_revenue.sql",
}

CONFIG_PATTERN = re.compile(r"\{\{\s*config\([^}]*\)\s*\}\}\s*", flags=re.IGNORECASE)
REF_PATTERN = re.compile(r"\{\{\s*ref\(['\"]([^'\"]+)['\"]\)\s*\}\}")


def compile_model_sql(sql_text):
    """Compile the small dbt subset used by this portfolio project."""
    compiled = CONFIG_PATTERN.sub("", sql_text)
    compiled = REF_PATTERN.sub(lambda match: match.group(1), compiled)
    return compiled.strip().rstrip(";")


def connect(database_path=None):
    connection = sqlite3.connect(database_path or ":memory:")
    connection.row_factory = sqlite3.Row
    return connection


def load_seed(connection, table_name, csv_path):
    with csv_path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    if not rows:
        raise ValueError(f"{csv_path} has no rows")

    columns = reader.fieldnames or []
    column_sql = ", ".join(f"{column} text" for column in columns)
    placeholders = ", ".join("?" for _ in columns)

    connection.execute(f"drop table if exists {table_name}")
    connection.execute(f"create table {table_name} ({column_sql})")
    connection.executemany(
        f"insert into {table_name} ({', '.join(columns)}) values ({placeholders})",
        [[row[column] for column in columns] for row in rows],
    )


def execute_model(connection, model_name):
    sql_text = MODEL_PATHS[model_name].read_text()
    compiled_sql = compile_model_sql(sql_text)

    connection.execute(f"drop table if exists {model_name}")
    connection.execute(f"create table {model_name} as {compiled_sql}")


def build_database(database_path=None):
    connection = connect(database_path)

    for table_name, csv_path in SEEDS.items():
        load_seed(connection, table_name, csv_path)

    for model_name in MODEL_ORDER:
        execute_model(connection, model_name)

    connection.commit()
    return connection


def scalar(connection, query):
    return connection.execute(query).fetchone()[0]


def run_quality_checks(connection):
    checks = [
        {
            "name": "raw order seed loaded",
            "query": "select count(*) from raw_orders",
            "expected": 10,
        },
        {
            "name": "order fact grain is unique",
            "query": "select count(*) - count(distinct order_id) from fct_orders",
            "expected": 0,
        },
        {
            "name": "customer dimension grain is unique",
            "query": "select count(*) - count(distinct customer_id) from dim_customers",
            "expected": 0,
        },
        {
            "name": "product dimension grain is unique",
            "query": "select count(*) - count(distinct product_id) from dim_products",
            "expected": 0,
        },
        {
            "name": "order revenue is never negative",
            "query": "select count(*) from fct_orders where order_revenue < 0",
            "expected": 0,
        },
        {
            "name": "fact revenue reconciles to enriched order revenue",
            "query": """
                select round(
                    (select sum(order_revenue) from fct_orders)
                    - (select sum(gross_revenue) from int_order_items_enriched),
                    2
                )
            """,
            "expected": 0.0,
        },
    ]

    failures = []
    for check in checks:
        actual = scalar(connection, check["query"])
        if actual != check["expected"]:
            failures.append({**check, "actual": actual})

    return failures


def fetch_dicts(connection, query):
    return [dict(row) for row in connection.execute(query).fetchall()]


def print_table(title, rows):
    print(f"\n{title}")
    if not rows:
        print("(no rows)")
        return

    columns = list(rows[0])
    widths = {
        column: max(len(column), *(len(str(row[column])) for row in rows))
        for column in columns
    }
    print(" | ".join(column.ljust(widths[column]) for column in columns))
    print("-+-".join("-" * widths[column] for column in columns))
    for row in rows:
        print(" | ".join(str(row[column]).ljust(widths[column]) for column in columns))


def run(dry_run=False, database_path=None):
    connection = build_database(database_path)
    failures = run_quality_checks(connection)
    if failures:
        messages = [f"{failure['name']}: expected {failure['expected']}, got {failure['actual']}" for failure in failures]
        raise AssertionError("; ".join(messages))

    if dry_run:
        print_table(
            "mart_daily_revenue",
            fetch_dicts(connection, "select * from mart_daily_revenue order by order_date"),
        )
        print_table(
            "mart_customer_lifetime_value",
            fetch_dicts(
                connection,
                """
                select customer_name, segment, order_count, lifetime_revenue, average_order_value, value_band
                from mart_customer_lifetime_value
                order by lifetime_revenue desc
                """,
            ),
        )
        print("\nquality checks: passed")

    return connection


def parse_args():
    parser = argparse.ArgumentParser(description="Build and validate the retail analytics engineering marts.")
    parser.add_argument("--dry-run", action="store_true", help="Print mart previews after validation.")
    parser.add_argument("--database-path", help="Optional SQLite database path to create.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(dry_run=args.dry_run, database_path=args.database_path)
