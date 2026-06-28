.PHONY: ci test dry-run-all up down airflow-logs postgres-shell secret-scan status

-include .env
export

PYTEST_TARGETS = project_1_csv_pipeline/tests project_2_api_pipeline/tests project_3_data_cleaning/tests project_4_json_pipeline/tests project_5_data_warehouse/tests project_6_ecommerce_pipeline/tests project_7_log_pipeline/tests

ci: test dry-run-all secret-scan

test:
	python -m pytest $(PYTEST_TARGETS) -q -p no:cacheprovider

dry-run-all:
	python project_1_csv_pipeline/scripts/etl_pipeline.py --dry-run
	python project_3_data_cleaning/scripts/cleaning_pipeline.py --dry-run
	python project_4_json_pipeline/scripts/json_pipeline.py --dry-run
	python project_5_data_warehouse/scripts/load_data.py --dry-run
	python project_6_ecommerce_pipeline/scripts/ecommerce_pipeline.py --dry-run
	python project_7_log_pipeline/scripts/log_pipeline.py --dry-run --no-state

up:
	docker compose up -d

down:
	docker compose down

airflow-logs:
	docker compose logs -f airflow-scheduler airflow-webserver

postgres-shell:
	docker compose exec postgres psql -U postgres -d data_projects

secret-scan:
	! rg -n "eroxzy|postgresql://postgres:password|postgresql://postgres:[^p]" -g '!venv/**' -g '!**/__pycache__/**' -g '!Makefile'

status:
	git status --short

