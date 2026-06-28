# Portfolio Roadmap

The seven core projects now have a job-ready foundation: runnable pipelines, project READMEs, tests, environment-based configuration, root Airflow DAGs, Docker Compose infrastructure, and CI validation.

## Current Status

| Area | Status |
| --- | --- |
| Seven project implementations | Complete |
| Project-level documentation | Complete |
| Root portfolio README | Complete |
| Local Postgres platform | Complete |
| Local Airflow platform | Complete |
| Airflow DAG discovery | Complete |
| Unit tests | Complete: `26 passed` |
| CI workflow | Complete |
| Cloud deployment | Intentionally skipped to avoid AWS billing |

## Completed Portfolio Projects

1. **Batch Sales ETL Platform**
   - CSV ingestion, transformation, Postgres loading, Docker, and Airflow.

2. **Resilient API Ingestion Pipeline**
   - API extraction, timeouts, error handling, payload validation, and retryable orchestration.

3. **Data Cleaning and Quality Pipeline**
   - Validation rules, accepted/rejected outputs, and testable data quality checks.

4. **Nested JSON Order Normalization**
   - Nested JSON parsing, order and order-item normalization, and relational loading.

5. **Dimensional Data Warehouse**
   - Customer, product, and date dimensions with a sales fact table.

6. **E-commerce Analytics Pipeline**
   - Multi-source joins, revenue metrics, product performance, and customer-level marts.

7. **Log Analytics and Performance Pipeline**
   - Log parsing, incremental state, event summaries, and operational analytics tables.

## Remaining Packaging Steps

These are the last non-engineering steps before using the portfolio in applications:

1. Commit the completed work to git.
2. Create a GitHub repository and push the `main` branch.
3. Add the GitHub URL to the resume.
4. Use the resume bullets in `docs/RESUME_AND_INTERVIEW_GUIDE.md`.
5. Keep the local demo commands in the README so interviewers can reproduce the work.

## Optional Future Upgrades

These would improve the portfolio, but they are not required for the first job-search version:

| Upgrade | Value | Billing Risk |
| --- | --- | --- |
| Local Spark job for logs or large CSVs | Adds distributed processing signal | None if run locally |
| dbt models on top of Postgres | Adds analytics engineering signal | None if run locally |
| Great Expectations or Soda checks | Stronger data quality story | None if run locally |
| Terraform examples only | Shows IaC awareness | None if not applied |
| Real AWS deployment | Strong cloud signal | Possible AWS charges |

## Recommended Next Move

Push this version to GitHub first. After that, the best next technical upgrade is a local Spark addition for the log analytics or performance pipeline, because it improves the resume signal without creating cloud costs.
