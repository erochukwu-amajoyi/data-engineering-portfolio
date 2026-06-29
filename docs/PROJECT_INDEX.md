# Project Index

This repository is organized as eight small but complete data engineering projects. The first seven fit into the shared local Airflow/Postgres platform; the eighth preserves a sanitized Azure Data Factory pipeline export as cloud proof without requiring live Azure billing.

## 1. Batch Sales ETL Platform

**Folder:** `project_1_csv_pipeline/`

**What it does:** Ingests raw sales CSV data, validates the schema, cleans types and missing values, and loads a `sales` table into Postgres.

**Why it matters:** This is the reference batch ETL project. It shows a common file ingestion workflow: extracting records, transforming data safely, loading into a database, and testing transformation logic.

**Key evidence:** project README, unit tests, dry-run mode, Postgres load path, Airflow DAG.

## 2. Resilient API Ingestion Pipeline

**Folder:** `project_2_api_pipeline/`

**What it does:** Ingests current weather data from an API, validates the payload, transforms it into tabular form, and prepares it for warehouse loading.

**Why it matters:** Many production pipelines depend on APIs. This project demonstrates defensive API handling with timeouts, HTTP error checks, configuration, and mocked tests that do not depend on live network access.

**Key evidence:** timeout handling, `raise_for_status`, payload validation, mocked unit tests, Airflow retry configuration.

## 3. Data Cleaning and Quality Pipeline

**Folder:** `project_3_data_cleaning/`

**What it does:** Cleans raw sales data and splits records into valid outputs and rejected outputs with rejection reasons.

**Why it matters:** Data engineers need to protect downstream analytics from bad records. This project shows practical data quality handling instead of silently dropping or corrupting rows.

**Key evidence:** valid/rejected datasets, rejection reasons, tests for quality rules, dry-run output.

## 4. Nested JSON Order Normalization

**Folder:** `project_4_json_pipeline/`

**What it does:** Reads nested order JSON and normalizes it into `orders` and `order_items` tables.

**Why it matters:** APIs and event streams often deliver nested payloads. This project shows how to convert semi-structured data into relational tables that analysts can query.

**Key evidence:** JSON validation, normalized outputs, referential checks, Postgres load path.

## 5. Dimensional Data Warehouse

**Folder:** `project_5_data_warehouse/`

**What it does:** Converts flat sales data into a star schema with `dim_customer`, `dim_product`, `dim_date`, and `fact_sales`.

**Why it matters:** Dimensional modeling is a core data warehousing skill. This project demonstrates fact/dimension design, surrogate keys, SQL DDL, and analytics-ready output.

**Key evidence:** SQL schema, star schema transforms, tests, Airflow DAG.

## 6. E-commerce Analytics Pipeline

**Folder:** `project_6_ecommerce_pipeline/`

**What it does:** Joins order, customer, and product sources into enriched order data and creates analytics marts for revenue, top products, and customer metrics.

**Why it matters:** This mirrors common analytics engineering work: joining multiple sources and producing business-facing datasets.

**Key evidence:** multi-source joins, KPI marts, repeat-customer metric, tests.

## 7. Log Analytics and Performance Pipeline

**Folder:** `project_7_log_pipeline/`

**What it does:** Parses application logs, captures user and product events, maintains incremental state, and creates operational analytics tables.

**Why it matters:** Log and event processing is a practical data engineering use case. This project adds incremental processing concepts and operational metrics.

**Key evidence:** regex parser, rejected-line handling, high-watermark state file, analytics marts.

## 8. Azure Data Factory Blob Pipeline

**Folder:** `project_8_azure_pipeline/`

**What it does:** Preserves a sanitized Azure Data Factory Copy pipeline that reads a customer churn CSV from Azure Blob Storage, applies explicit tabular mappings, and writes to a delimited-text sink dataset.

**Why it matters:** This demonstrates cloud data engineering experience without keeping billable resources alive. The project keeps ADF pipeline, dataset and linked-service artifacts in source control, removes account-specific credentials, and validates the export locally.

**Key evidence:** ADF pipeline JSON, Blob Storage linked service, source/sink dataset schemas, mapping validation script, public-safe teardown notes.

## Shared Platform Evidence

Across the repository:

- Airflow DAG wrappers live in `dags/`.
- Local Postgres and Airflow run through `docker-compose.yml`.
- `make ci` runs tests, dry runs, ADF export validation, and the secret scan.
- GitHub Actions runs the CI workflow.
- `.env.example` documents local configuration.
