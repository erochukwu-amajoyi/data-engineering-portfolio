import argparse
import logging
import os
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
REQUIRED_COLUMNS = {"order_id", "customer_name", "product", "amount", "order_date"}
logger = logging.getLogger(__name__)


def configure_logging():
    if logging.getLogger().handlers:
        return

    log_dir = PROJECT_ROOT / "logs"
    try:
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "pipeline.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    except OSError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logger.warning("File logging unavailable; using console logging instead")


def resolve_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path

    repo_candidate = REPO_ROOT / path
    if repo_candidate.exists() or repo_candidate.parent.exists():
        return repo_candidate

    return PROJECT_ROOT / path


def validate_columns(df):
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")


def extract_data(file_path):
    input_path = resolve_path(file_path)
    df = pd.read_csv(input_path)
    logger.info("Extracted %s rows from %s", len(df), input_path)
    return df


def clean_data(df):
    validate_columns(df)

    cleaned = df.copy().drop_duplicates().reset_index(drop=True)
    cleaned["customer_name"] = cleaned["customer_name"].fillna("Unknown")
    cleaned["customer_name"] = cleaned["customer_name"].astype(str).str.strip()
    cleaned["product"] = cleaned["product"].fillna("").astype(str).str.strip()
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], errors="coerce")

    logger.info("Cleaned and standardized %s rows", len(cleaned))
    return cleaned


def get_rejection_reasons(row):
    reasons = []

    if pd.isna(row["order_id"]):
        reasons.append("missing_order_id")
    if not row["product"]:
        reasons.append("missing_product")
    if pd.isna(row["amount"]):
        reasons.append("missing_or_invalid_amount")
    elif row["amount"] < 0:
        reasons.append("negative_amount")
    if pd.isna(row["order_date"]):
        reasons.append("invalid_order_date")

    return ";".join(reasons)


def split_valid_rejected(df):
    quality_checked = df.copy()
    quality_checked["rejection_reason"] = quality_checked.apply(get_rejection_reasons, axis=1)

    rejected = quality_checked[quality_checked["rejection_reason"] != ""].copy()
    valid = quality_checked[quality_checked["rejection_reason"] == ""].copy()
    valid = valid.drop(columns=["rejection_reason"]).reset_index(drop=True)
    rejected = rejected.reset_index(drop=True)

    logger.info("Quality check complete: %s valid rows, %s rejected rows", len(valid), len(rejected))
    return valid, rejected


def save_outputs(valid_df, rejected_df, clean_output_path, rejected_output_path):
    clean_path = resolve_path(clean_output_path)
    rejected_path = resolve_path(rejected_output_path)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path.parent.mkdir(parents=True, exist_ok=True)

    valid_df.to_csv(clean_path, index=False)
    rejected_df.to_csv(rejected_path, index=False)
    logger.info("Wrote clean output to %s", clean_path)
    logger.info("Wrote rejected output to %s", rejected_path)


def run_pipeline(input_path=None, clean_output_path=None, rejected_output_path=None, dry_run=False):
    configure_logging()
    input_path = input_path or os.getenv(
        "DATA_QUALITY_INPUT_PATH",
        "project_3_data_cleaning/data/raw_data.csv",
    )
    clean_output_path = clean_output_path or os.getenv(
        "DATA_QUALITY_CLEAN_OUTPUT_PATH",
        "project_3_data_cleaning/data/clean_data.csv",
    )
    rejected_output_path = rejected_output_path or os.getenv(
        "DATA_QUALITY_REJECTED_OUTPUT_PATH",
        "project_3_data_cleaning/data/rejected_records.csv",
    )

    raw_df = extract_data(input_path)
    cleaned_df = clean_data(raw_df)
    valid_df, rejected_df = split_valid_rejected(cleaned_df)

    if dry_run:
        print("Clean records:")
        print(valid_df.to_string(index=False))
        print("\nRejected records:")
        print(rejected_df.to_string(index=False))
        return valid_df, rejected_df

    save_outputs(valid_df, rejected_df, clean_output_path, rejected_output_path)
    logger.info("Data quality pipeline executed successfully")
    return valid_df, rejected_df


def parse_args():
    parser = argparse.ArgumentParser(description="Run the sales data quality pipeline.")
    parser.add_argument("--input-path", default=None, help="Raw CSV input path.")
    parser.add_argument("--clean-output-path", default=None, help="Clean CSV output path.")
    parser.add_argument("--rejected-output-path", default=None, help="Rejected CSV output path.")
    parser.add_argument("--dry-run", action="store_true", help="Print outputs without writing files.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        input_path=args.input_path,
        clean_output_path=args.clean_output_path,
        rejected_output_path=args.rejected_output_path,
        dry_run=args.dry_run,
    )
