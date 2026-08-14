"""Generate realistic General Insurance portfolio sample data."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import CHANNELS, DATA_DIR, PRODUCT_LINES, REGIONS, SAMPLE_DATA_PATH

logger = logging.getLogger("actuarial_platform")


def generate_sample_portfolio(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic insurance portfolio with intentional data quality issues.

    Args:
        n_rows: Number of policy records to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with required portfolio columns and injected quality issues.
    """
    rng = np.random.default_rng(seed)
    n = n_rows

    start_dates = pd.date_range("2022-01-01", periods=730, freq="D")
    policy_starts = rng.choice(start_dates, size=n)
    policy_durations = rng.integers(180, 366, size=n)
    policy_ends = policy_starts + pd.to_timedelta(policy_durations, unit="D")

    exposure = rng.uniform(0.25, 1.0, size=n).round(3)
    age = rng.integers(18, 75, size=n)
    vehicle_age = rng.integers(0, 20, size=n)

    product_line = rng.choice(PRODUCT_LINES, size=n, p=[0.45, 0.25, 0.20, 0.10])
    region = rng.choice(REGIONS, size=n)
    channel = rng.choice(CHANNELS, size=n, p=[0.35, 0.25, 0.20, 0.20])

    base_premium = {
        "Motor": 850,
        "Home": 620,
        "Commercial": 1450,
        "Liability": 980,
    }
    premium = np.array([base_premium[p] for p in product_line])
    premium = premium * rng.uniform(0.7, 1.4, size=n) * exposure
    premium = premium.round(2)

    claim_rate = np.where(product_line == "Motor", 0.12, 0.08)
    claim_rate = claim_rate + (age > 65) * 0.03
    claim_count = rng.poisson(claim_rate * exposure).astype(int)

    severity_base = {
        "Motor": 3200,
        "Home": 4800,
        "Commercial": 12500,
        "Liability": 7600,
    }
    claim_amount = np.zeros(n)
    for i in range(n):
        if claim_count[i] > 0:
            base = severity_base[product_line[i]]
            claim_amount[i] = rng.lognormal(np.log(base), 0.6) * claim_count[i]
        claim_amount[i] = round(claim_amount[i], 2)

    df = pd.DataFrame(
        {
            "PolicyID": [f"POL-{100000 + i}" for i in range(n)],
            "CustomerID": [f"CUST-{50000 + rng.integers(0, 3000)}" for _ in range(n)],
            "ProductLine": product_line,
            "Region": region,
            "Channel": channel,
            "PolicyStartDate": policy_starts,
            "PolicyEndDate": policy_ends,
            "Exposure": exposure,
            "Premium": premium,
            "ClaimCount": claim_count,
            "ClaimAmount": claim_amount,
            "Age": age,
            "VehicleAge": vehicle_age,
        }
    )

    df = _inject_data_quality_issues(df, rng)
    logger.info("Generated sample portfolio with %d rows", len(df))
    return df


def _inject_data_quality_issues(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Inject intentional data quality issues for validation demos."""
    df = df.copy()
    n = len(df)

    # Duplicate PolicyIDs
    dup_indices = rng.choice(n, size=15, replace=False)
    dup_rows = df.iloc[dup_indices].copy()
    dup_rows["Premium"] = dup_rows["Premium"] * rng.uniform(0.9, 1.1, size=len(dup_rows))
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Missing values
    for col, count in [("Premium", 25), ("ClaimAmount", 18), ("Age", 12), ("Region", 8)]:
        idx = rng.choice(len(df), size=count, replace=False)
        df.loc[df.index[idx], col] = np.nan

    # Negative premiums
    idx = rng.choice(len(df), size=10, replace=False)
    df.loc[df.index[idx], "Premium"] = -df.loc[df.index[idx], "Premium"].abs()

    # Negative claim amounts
    idx = rng.choice(len(df), size=8, replace=False)
    df.loc[df.index[idx], "ClaimAmount"] = -500.0

    # Zero/negative exposure
    idx = rng.choice(len(df), size=12, replace=False)
    df.loc[df.index[idx], "Exposure"] = 0.0
    idx = rng.choice(len(df), size=5, replace=False)
    df.loc[df.index[idx], "Exposure"] = -0.1

    # End date before start date
    idx = rng.choice(len(df), size=10, replace=False)
    df.loc[df.index[idx], "PolicyEndDate"] = df.loc[df.index[idx], "PolicyStartDate"] - pd.Timedelta(days=30)

    # Negative claim count
    idx = rng.choice(len(df), size=6, replace=False)
    df.loc[df.index[idx], "ClaimCount"] = -1

    return df


def save_sample_data(path: Path | None = None, n_rows: int = 5000) -> Path:
    """Generate and save sample portfolio CSV."""
    output_path = path or SAMPLE_DATA_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_sample_portfolio(n_rows=n_rows)
    df.to_csv(output_path, index=False)
    logger.info("Saved sample data to %s", output_path)
    return output_path


if __name__ == "__main__":
    save_sample_data()
