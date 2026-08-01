# Analytics Engineering Portfolio Track

This track positions the repository for analytics engineering roles: SQL modelling, tested transformations, dimensional design, business-facing marts, documentation, and data quality.

## Recommended Project Set

| Project | Why It Fits Analytics Engineering | Evidence |
| --- | --- | --- |
| [Retail Analytics Engineering with dbt](../project_9_analytics_engineering/) | Shows dbt-compatible modelling from raw seeds through staging, intermediate models, dimensions, facts, and marts. | SQL models, schema tests, singular tests, lineage through `ref()`, local validation runner |
| [Dimensional Data Warehouse](../project_5_data_warehouse/) | Demonstrates star-schema modelling, fact/dimension design, and warehouse loading. | SQL DDL, surrogate keys, `fact_sales`, dimensions, tests |
| [E-commerce Analytics Pipeline](../project_6_ecommerce_pipeline/) | Converts operational order, customer, and product data into KPI-ready marts. | Daily revenue, top products, customer metrics, repeat-customer logic |
| [Data Cleaning and Quality Pipeline](../project_3_data_cleaning/) | Shows that bad source records are handled before they affect downstream reporting. | Validation rules, rejected records, rejection reasons, test coverage |

## Related Academic Project

| Project | Analytics Engineering Relevance | Evidence |
| --- | --- | --- |
| [Missing Data Handling Dissertation Notebook](https://hullacuk-my.sharepoint.com/:u:/g/personal/e_amajoyi-2024_hull_ac_uk/IQDo_zj5zMx3T76Eipng4kf3Aad_r4IiYeJnC44BEn5osO8?e=Qafa4K) | Connects data quality, missing-value handling, model readiness, and validation. Useful for roles where analytics data must be reliable before business or ML use. | Jupyter notebook with missing-data experiments and evaluation |

## Technical Focus

For analytics engineering roles, this track emphasizes:

- SQL transformations and warehouse modelling.
- dbt-compatible project structure, tests, docs, and lineage.
- Fact and dimension tables.
- Business metrics such as daily revenue, customer value, product performance, and repeat-customer logic.
- Data quality checks that prevent unreliable reporting.
- Python, Airflow, and CI/CD as supporting engineering skills.

## Cost-Safe Stack

| Layer | Portfolio Implementation | What It Shows |
| --- | --- | --- |
| Ingestion | CSV/API/Python pipelines already in the repository | Can land and validate raw data |
| Warehouse | Local Postgres and local SQLite validation | Understands relational warehouses without cloud billing |
| Transformation | SQL and dbt-compatible model files | Can build analytics-ready datasets |
| Testing | `pytest`, dbt-style schema tests, singular SQL tests | Treats data models as production assets |
| Documentation | Model YAML, README files, project index | Can make data assets understandable |
| Cloud-ready path | Snowflake profile template with environment variables | Knows how local patterns map to managed warehouses |
