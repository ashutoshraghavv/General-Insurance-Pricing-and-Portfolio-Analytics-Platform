"""Data loading utilities for CSV, XLSX, and sample datasets."""

import logging
from io import BytesIO
from typing import BinaryIO, Optional, Union

import pandas as pd

from src.config import REQUIRED_COLUMNS, SAMPLE_DATA_PATH
from src.data.generator import save_sample_data

logger = logging.getLogger("actuarial_platform")


def load_csv(uploaded_file: Union[BinaryIO, str]) -> pd.DataFrame:
    """Load portfolio data from a CSV file."""
    df = pd.read_csv(uploaded_file)
    logger.info("Loaded CSV with %d rows, %d columns", len(df), len(df.columns))
    return df


def load_xlsx(uploaded_file: Union[BinaryIO, str]) -> pd.DataFrame:
    """Load portfolio data from an XLSX file."""
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    logger.info("Loaded XLSX with %d rows, %d columns", len(df), len(df.columns))
    return df


def load_sample_dataset() -> pd.DataFrame:
    """Load the bundled sample portfolio dataset, generating if missing."""
    if not SAMPLE_DATA_PATH.exists():
        save_sample_data()
    df = pd.read_csv(SAMPLE_DATA_PATH, parse_dates=["PolicyStartDate", "PolicyEndDate"])
    logger.info("Loaded sample dataset with %d rows", len(df))
    return df


def get_schema_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return schema preview with dtypes and missing counts."""
    summary = pd.DataFrame(
        {
            "Column": df.columns,
            "Dtype": df.dtypes.astype(str).values,
            "Non-Null": df.notna().sum().values,
            "Missing": df.isna().sum().values,
            "Missing %": (df.isna().sum() / len(df) * 100).round(2).values,
        }
    )
    return summary


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing value summary for columns with any nulls."""
    missing = df.isna().sum()
    missing = missing[missing > 0].reset_index()
    missing.columns = ["Column", "Missing Count"]
    missing["Missing %"] = (missing["Missing Count"] / len(df) * 100).round(2)
    return missing.sort_values("Missing Count", ascending=False)


def validate_required_columns(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Check whether all required columns are present."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0, missing


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date columns if present."""
    df = df.copy()
    for col in ["PolicyStartDate", "PolicyEndDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def load_uploaded_file(
    uploaded_file, file_type: str
) -> Optional[pd.DataFrame]:
    """
    Load an uploaded file based on type.

    Args:
        uploaded_file: Streamlit UploadedFile object.
        file_type: 'csv' or 'xlsx'.

    Returns:
        Loaded DataFrame or None on failure.
    """
    try:
        if file_type == "csv":
            df = load_csv(uploaded_file)
        elif file_type == "xlsx":
            df = load_xlsx(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return parse_dates(df)
    except Exception as exc:
        logger.error("Failed to load file: %s", exc)
        raise
