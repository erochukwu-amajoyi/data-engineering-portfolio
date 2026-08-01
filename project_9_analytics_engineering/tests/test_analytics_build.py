from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_local_analytics import build_database, compile_model_sql, run_quality_checks  # noqa: E402


def test_local_build_creates_expected_revenue_mart():
    connection = build_database()

    total_revenue = connection.execute("select round(sum(revenue), 2) from mart_daily_revenue").fetchone()[0]
    top_day = connection.execute(
        """
        select order_date, revenue
        from mart_daily_revenue
        order by revenue desc
        limit 1
        """
    ).fetchone()

    assert total_revenue == 2780.0
    assert dict(top_day) == {"order_date": "2026-01-07", "revenue": 935.0}


def test_customer_lifetime_value_segments_customers():
    connection = build_database()

    top_customer = connection.execute(
        """
        select customer_name, order_count, lifetime_revenue, value_band
        from mart_customer_lifetime_value
        order by lifetime_revenue desc
        limit 1
        """
    ).fetchone()

    assert dict(top_customer) == {
        "customer_name": "Liam Chen",
        "order_count": 2,
        "lifetime_revenue": 835.0,
        "value_band": "high_value",
    }


def test_quality_checks_pass():
    connection = build_database()

    assert run_quality_checks(connection) == []


def test_dbt_ref_syntax_compiles_for_local_validation():
    sql_text = (PROJECT_ROOT / "models" / "marts" / "mart_daily_revenue.sql").read_text()
    compiled = compile_model_sql(sql_text)

    assert "{{" not in compiled
    assert "ref(" not in compiled
    assert "from fct_orders" in compiled
