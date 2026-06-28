import argparse
import json
import logging
import os
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
LOG_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.+)")
logger = logging.getLogger(__name__)

PARSED_COLUMNS = ["log_time", "log_level", "message", "user_id", "product_id"]
REJECTED_COLUMNS = ["line_number", "raw_line", "rejection_reason"]


def configure_logging():
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def resolve_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path

    repo_candidate = REPO_ROOT / path
    if repo_candidate.exists() or repo_candidate.parent.exists():
        return repo_candidate

    return PROJECT_ROOT / path


def extract_data(file_path):
    input_path = resolve_path(file_path)
    lines = input_path.read_text(encoding="utf-8").splitlines()
    logger.info("Extracted %s log lines from %s", len(lines), input_path)
    return lines


def parse_log_line(raw_line):
    match = LOG_PATTERN.match(raw_line.strip())
    if not match:
        raise ValueError("unparseable_log_line")

    log_time, log_level, message = match.groups()
    user_match = re.search(r"user_id=(\d+)", message)
    product_match = re.search(r"product_id=(\d+)", message)

    user_id = int(user_match.group(1)) if user_match else None
    product_id = int(product_match.group(1)) if product_match else None

    clean_message = re.sub(r"user_id=\d+", "", message)
    clean_message = re.sub(r"product_id=\d+", "", clean_message).strip()

    return {
        "log_time": log_time,
        "log_level": log_level,
        "message": clean_message,
        "user_id": user_id,
        "product_id": product_id,
    }


def parse_logs(logs):
    parsed_rows = []
    rejected_rows = []

    for line_number, raw_line in enumerate(logs, start=1):
        try:
            parsed_rows.append(parse_log_line(raw_line))
        except ValueError as error:
            rejected_rows.append(
                {
                    "line_number": line_number,
                    "raw_line": raw_line.strip(),
                    "rejection_reason": str(error),
                }
            )

    parsed = pd.DataFrame(parsed_rows, columns=PARSED_COLUMNS)
    rejected = pd.DataFrame(rejected_rows, columns=REJECTED_COLUMNS)
    logger.info("Parsed %s log lines and rejected %s", len(parsed), len(rejected))
    return parsed, rejected


def transform_data(df):
    transformed = df.copy()
    if transformed.empty:
        transformed["log_time"] = pd.to_datetime(transformed.get("log_time", []))
        return transformed

    transformed["log_time"] = pd.to_datetime(transformed["log_time"], errors="raise")
    transformed["log_level"] = transformed["log_level"].str.upper()
    return transformed.sort_values("log_time").reset_index(drop=True)


def read_state(state_path):
    resolved = resolve_path(state_path)
    if not resolved.exists():
        return None

    state = json.loads(resolved.read_text(encoding="utf-8"))
    last_log_time = state.get("last_log_time")
    return pd.Timestamp(last_log_time) if last_log_time else None


def filter_incremental_logs(df, state_path):
    last_log_time = read_state(state_path)
    if last_log_time is None or df.empty:
        return df.copy().reset_index(drop=True)

    filtered = df[df["log_time"] > last_log_time].copy().reset_index(drop=True)
    logger.info("Filtered logs after %s: %s rows remain", last_log_time, len(filtered))
    return filtered


def update_state(df, state_path):
    if df.empty:
        return

    resolved = resolve_path(state_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    state = {"last_log_time": df["log_time"].max().isoformat()}
    resolved.write_text(json.dumps(state, indent=2), encoding="utf-8")
    logger.info("Updated log state at %s", resolved)


def generate_analytics(df):
    parsed_logs = df.copy().reset_index(drop=True)

    log_level_counts = (
        parsed_logs.groupby("log_level", as_index=False)
        .size()
        .rename(columns={"size": "event_count"})
        .sort_values("event_count", ascending=False)
        .reset_index(drop=True)
    )

    user_activity = (
        parsed_logs.dropna(subset=["user_id"])
        .groupby("user_id", as_index=False)
        .agg(event_count=("message", "size"), first_seen=("log_time", "min"), last_seen=("log_time", "max"))
        .sort_values("event_count", ascending=False)
        .reset_index(drop=True)
    )

    product_events = (
        parsed_logs.dropna(subset=["product_id"])
        .groupby("product_id", as_index=False)
        .agg(event_count=("message", "size"), first_seen=("log_time", "min"), last_seen=("log_time", "max"))
        .sort_values("event_count", ascending=False)
        .reset_index(drop=True)
    )

    marts = {
        "parsed_logs": parsed_logs,
        "log_level_counts": log_level_counts,
        "user_activity": user_activity,
        "product_events": product_events,
    }
    logger.info("Generated log analytics marts: %s", ", ".join(marts))
    return marts


def load_data(marts, database_url=None):
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/data_projects",
    )
    engine = create_engine(database_url)

    marts["parsed_logs"].to_sql("parsed_logs", engine, if_exists="append", index=False)
    for table_name in ["log_level_counts", "user_activity", "product_events"]:
        marts[table_name].to_sql(table_name, engine, if_exists="replace", index=False)
    logger.info("Loaded log analytics marts to Postgres")


def run_pipeline(input_path=None, state_path=None, dry_run=False, use_state=True):
    configure_logging()
    input_path = input_path or os.getenv("LOG_INPUT_PATH", "project_7_log_pipeline/data/app.log")
    state_path = state_path or os.getenv("LOG_STATE_PATH", "project_7_log_pipeline/state/log_state.json")

    logs = extract_data(input_path)
    parsed, rejected = parse_logs(logs)
    transformed = transform_data(parsed)
    incremental = filter_incremental_logs(transformed, state_path) if use_state else transformed
    marts = generate_analytics(incremental)

    if dry_run:
        for table_name, df in marts.items():
            print(f"\n{table_name}:")
            print(df.to_string(index=False))
        if not rejected.empty:
            print("\nrejected_logs:")
            print(rejected.to_string(index=False))
        return marts, rejected

    load_data(marts)
    if use_state:
        update_state(incremental, state_path)
    logger.info("Log analytics pipeline completed successfully")
    return marts, rejected


def parse_args():
    parser = argparse.ArgumentParser(description="Parse logs incrementally and build analytics marts.")
    parser.add_argument("--input-path", default=None, help="Application log input path.")
    parser.add_argument("--state-path", default=None, help="Incremental state file path.")
    parser.add_argument("--dry-run", action="store_true", help="Print outputs without loading or writing state.")
    parser.add_argument("--no-state", action="store_true", help="Ignore incremental state for this run.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        input_path=args.input_path,
        state_path=args.state_path,
        dry_run=args.dry_run,
        use_state=not args.no_state,
    )
