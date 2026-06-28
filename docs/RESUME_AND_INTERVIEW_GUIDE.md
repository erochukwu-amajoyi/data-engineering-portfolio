# Resume and Interview Guide

Use this document to translate the repository into resume bullets, LinkedIn wording, and interview talking points.

## Short Portfolio Summary

Built a seven-project data engineering portfolio with Python, pandas, Postgres, Airflow, Docker Compose, pytest, and GitHub Actions. The projects cover batch ingestion, API ingestion, data quality, JSON normalization, dimensional modeling, analytics marts, and incremental log processing, all runnable locally without cloud billing.

## Resume Bullets

Choose two or three bullets depending on space:

- Built a local data engineering platform with Airflow, Postgres, Docker Compose, pytest, and GitHub Actions to orchestrate and validate seven ETL/ELT pipelines.
- Developed batch, API, JSON, warehouse, e-commerce analytics, and log-processing pipelines with environment-based configuration and no hard-coded secrets.
- Designed a dimensional warehouse with customer, product, and date dimensions plus a sales fact table for analytics-ready reporting.
- Implemented data quality workflows that separate valid and rejected records with explicit rejection reasons and unit-tested validation logic.
- Created incremental log analytics using parsed application events, high-watermark state, and operational summary marts.
- Added CI validation covering unit tests, pipeline dry runs, and a repository secret scan.

## LinkedIn or Portfolio Description

I built a local-first data engineering portfolio that simulates production workflows without requiring paid cloud infrastructure. It includes seven pipeline projects orchestrated with Airflow, backed by Postgres, containerized with Docker Compose, and validated through pytest and GitHub Actions. The projects cover common data engineering patterns including batch file ingestion, API ingestion, data quality, nested JSON normalization, dimensional modeling, analytics marts, and incremental log processing.

## Interview Talking Points

### Why this portfolio is useful

It shows more than isolated scripts. Each project has a repeatable run path, configuration, tests, documentation, and orchestration. The shared Docker Compose platform lets the work run locally while still demonstrating production-style habits.

### Why no AWS deployment yet

The cloud deployment was intentionally skipped to avoid unnecessary billing. The platform uses local Airflow and Postgres so the engineering can be reviewed and reproduced safely. Terraform can be added later as an example-only layer or used for real deployment when cloud costs are acceptable.

### How to demo it

1. Run `make ci` to show tests and dry runs passing.
2. Run `make up` to start Airflow and Postgres.
3. Open Airflow at `http://localhost:8081`.
4. Show the seven DAGs in the Airflow UI.
5. Trigger one pipeline and query the output table in Postgres.

### Strongest project to explain first

Start with the **Dimensional Data Warehouse** or the **E-commerce Analytics Pipeline**. They are easiest for recruiters and interviewers to connect to business value because they create reporting-ready tables and KPIs.

### Best technical deep dive

Use the **Log Analytics and Performance Pipeline**. It gives you a stronger engineering discussion around parsing, state, rejected records, incremental processing, and operational metrics.

## Skills Map

| Skill | Where It Appears |
| --- | --- |
| Python ETL | All seven projects |
| pandas | Transformations and marts |
| SQL/Postgres | Warehouse and load targets |
| Airflow | Root `dags/` folder |
| Docker Compose | Local Airflow/Postgres platform |
| Testing | Project `tests/` folders |
| CI/CD | `.github/workflows/ci.yml` |
| Data quality | Project 3 and shared validation patterns |
| Dimensional modeling | Project 5 |
| Incremental processing | Project 7 |

## Suggested GitHub Repository Description

Data engineering portfolio with 7 local-first ETL/ELT projects using Python, pandas, Postgres, Airflow, Docker Compose, pytest, and GitHub Actions.
