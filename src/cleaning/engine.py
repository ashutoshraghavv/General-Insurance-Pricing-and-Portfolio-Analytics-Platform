"""Portfolio data cleaning engine."""

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("actuarial_platform")


@dataclass
class CleaningResult:
    """Result of the cleaning pipeline."""

    cleaned_df: pd.DataFrame
    before_metrics: dict[str, Any]
    after_metrics: dict[str, Any]
    actions: list[str] = field(default_factory=list)
    outlier_flags: pd.Series = field(default_factory=pd.Series)

    @property
    def rows_removed(self) -> int:
        """Number of rows removed during cleaning."""
        return self.before_metrics.get("row_count", 0) - self.after_metrics.get(
            "row_count", 0
        )


def _compute_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute summary metrics for before/after comparison."""
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_total": int(df.isna().sum().sum()),
        "duplicate_policy_ids": int(df.duplicated(subset=["PolicyID"]).sum())
        if "PolicyID" in df.columns
        else 0,
        "negative_premiums": int((df["Premium"] < 0).sum()) if "Premium" in df.columns else 0,
        "invalid_exposure": int((df["Exposure"] <= 0).sum())
        if "Exposure" in df.columns
        else 0,
    }


def _correct_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Correct column data types."""
    df = df.copy()
    numeric_cols = [
        "Exposure",
        "Premium",
        "ClaimCount",
        "ClaimAmount",
        "Age",
        "VehicleAge",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["PolicyStartDate", "PolicyEndDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["ProductLine", "Region", "Channel", "PolicyID", "CustomerID"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df


def _flag_outliers(df: pd.DataFrame) -> pd.Series:
    """Flag statistical outliers in Premium and ClaimAmount using IQR."""
    flags = pd.Series(False, index=df.index)
    for col in ["Premium", "ClaimAmount"]:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if len(series) < 10:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
        flags |= (df[col] < lower) | (df[col] > upper)
    return flags


def clean_portfolio(df: pd.DataFrame) -> CleaningResult:
    """
    Clean portfolio data through deduplication, imputation, correction, and outlier flagging.

    Steps:
        1. Datatype correction
        2. Remove duplicate PolicyIDs (keep first)
        3. Remove invalid exposure rows
        4. Fix negative premiums/claims (set to NaN then impute)
        5. Fix invalid date ranges
        6. Fix negative claim counts
        7. Impute missing numeric values with median
        8. Impute missing categoricals with mode
        9. Flag outliers
    """
    actions: list[str] = []
    before_metrics = _compute_metrics(df)

    cleaned = _correct_dtypes(df)
    actions.append("Corrected data types")

    if "PolicyID" in cleaned.columns:
        n_before = len(cleaned)
        cleaned = cleaned.drop_duplicates(subset=["PolicyID"], keep="first")
        removed = n_before - len(cleaned)
        if removed:
            actions.append(f"Removed {removed} duplicate PolicyID rows")

    if "Exposure" in cleaned.columns:
        n_before = len(cleaned)
        cleaned = cleaned[cleaned["Exposure"] > 0]
        removed = n_before - len(cleaned)
        if removed:
            actions.append(f"Removed {removed} rows with Exposure <= 0")

    if "PolicyStartDate" in cleaned.columns and "PolicyEndDate" in cleaned.columns:
        invalid = cleaned["PolicyEndDate"] < cleaned["PolicyStartDate"]
        if invalid.any():
            cleaned.loc[invalid, "PolicyEndDate"] = cleaned.loc[
                invalid, "PolicyStartDate"
            ] + pd.Timedelta(days=365)
            actions.append(f"Corrected {invalid.sum()} invalid date ranges")

    if "Premium" in cleaned.columns:
        neg = cleaned["Premium"] < 0
        if neg.any():
            cleaned.loc[neg, "Premium"] = np.nan
            actions.append(f"Nullified {neg.sum()} negative premiums for imputation")

    if "ClaimAmount" in cleaned.columns:
        neg = cleaned["ClaimAmount"] < 0
        if neg.any():
            cleaned.loc[neg, "ClaimAmount"] = 0.0
            actions.append(f"Set {neg.sum()} negative claim amounts to zero")

    if "ClaimCount" in cleaned.columns:
        neg = cleaned["ClaimCount"] < 0
        if neg.any():
            cleaned.loc[neg, "ClaimCount"] = 0
            actions.append(f"Set {neg.sum()} negative claim counts to zero")

    numeric_cols = ["Exposure", "Premium", "ClaimCount", "ClaimAmount", "Age", "VehicleAge"]
    for col in numeric_cols:
        if col in cleaned.columns and cleaned[col].isna().any():
            median_val = cleaned[col].median()
            n_miss = cleaned[col].isna().sum()
            cleaned[col] = cleaned[col].fillna(median_val)
            actions.append(f"Imputed {n_miss} missing values in {col} with median")

    cat_cols = ["ProductLine", "Region", "Channel"]
    for col in cat_cols:
        if col in cleaned.columns and cleaned[col].isna().any():
            mode_val = cleaned[col].mode()
            fill_val = mode_val.iloc[0] if len(mode_val) else "Unknown"
            n_miss = cleaned[col].isna().sum()
            cleaned[col] = cleaned[col].fillna(fill_val)
            actions.append(f"Imputed {n_miss} missing values in {col} with mode")

    outlier_flags = _flag_outliers(cleaned)
    n_outliers = int(outlier_flags.sum())
    if n_outliers:
        actions.append(f"Flagged {n_outliers} outlier records (retained)")

    cleaned = cleaned.reset_index(drop=True)
    after_metrics = _compute_metrics(cleaned)

    logger.info(
        "Cleaning complete: %d -> %d rows, %d actions",
        before_metrics["row_count"],
        after_metrics["row_count"],
        len(actions),
    )

    return CleaningResult(
        cleaned_df=cleaned,
        before_metrics=before_metrics,
        after_metrics=after_metrics,
        actions=actions,
        outlier_flags=outlier_flags,
    )
