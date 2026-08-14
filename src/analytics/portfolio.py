"""Portfolio analytics and KPI engine."""

import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd

logger = logging.getLogger("actuarial_platform")


@dataclass
class PortfolioKPIs:
    """Portfolio-level key performance indicators."""

    written_premium: float
    total_claims: float
    loss_ratio: float
    claim_frequency: float
    claim_severity: float
    pure_premium: float
    exposure: float
    policy_count: int

    def to_dict(self) -> dict:
        """Convert KPIs to dictionary."""
        return {
            "Written Premium": self.written_premium,
            "Total Claims": self.total_claims,
            "Loss Ratio (%)": self.loss_ratio,
            "Claim Frequency": self.claim_frequency,
            "Claim Severity": self.claim_severity,
            "Pure Premium": self.pure_premium,
            "Exposure": self.exposure,
            "Policy Count": self.policy_count,
        }


def calculate_kpis(df: pd.DataFrame, pure_premium: Optional[float] = None) -> PortfolioKPIs:
    """
    Calculate portfolio-level KPIs.

    Args:
        df: Cleaned portfolio DataFrame.
        pure_premium: Optional modeled pure premium; uses empirical if not provided.

    Returns:
        PortfolioKPIs dataclass.
    """
    written_premium = float(df["Premium"].sum())
    total_claims = float(df["ClaimAmount"].sum())
    exposure = float(df["Exposure"].sum())
    policy_count = len(df)
    total_claim_count = float(df["ClaimCount"].sum())

    loss_ratio = (total_claims / written_premium * 100) if written_premium > 0 else 0.0
    claim_frequency = (total_claim_count / exposure) if exposure > 0 else 0.0
    claim_severity = (total_claims / total_claim_count) if total_claim_count > 0 else 0.0

    if pure_premium is None:
        pure_premium = claim_frequency * claim_severity

    kpis = PortfolioKPIs(
        written_premium=round(written_premium, 2),
        total_claims=round(total_claims, 2),
        loss_ratio=round(loss_ratio, 2),
        claim_frequency=round(claim_frequency, 6),
        claim_severity=round(claim_severity, 2),
        pure_premium=round(pure_premium, 2),
        exposure=round(exposure, 2),
        policy_count=policy_count,
    )
    logger.info("KPIs calculated: LR=%.2f%%, policies=%d", kpis.loss_ratio, policy_count)
    return kpis


def segment_profitability(
    df: pd.DataFrame, segment_col: str, pure_premium: Optional[float] = None
) -> pd.DataFrame:
    """Calculate profitability metrics by segment."""
    grouped = (
        df.groupby(segment_col)
        .agg(
            WrittenPremium=("Premium", "sum"),
            TotalClaims=("ClaimAmount", "sum"),
            Exposure=("Exposure", "sum"),
            ClaimCount=("ClaimCount", "sum"),
            PolicyCount=("PolicyID", "count"),
        )
        .reset_index()
    )
    grouped["LossRatio"] = (
        grouped["TotalClaims"] / grouped["WrittenPremium"] * 100
    ).round(2)
    grouped["ClaimFrequency"] = (
        grouped["ClaimCount"] / grouped["Exposure"]
    ).round(6)
    grouped["ClaimSeverity"] = (
        grouped["TotalClaims"] / grouped["ClaimCount"].replace(0, float("nan"))
    ).round(2)
    grouped["PurePremium"] = (grouped["ClaimFrequency"] * grouped["ClaimSeverity"]).round(
        2
    )
    grouped["ProfitMargin"] = (
        (grouped["WrittenPremium"] - grouped["TotalClaims"])
        / grouped["WrittenPremium"]
        * 100
    ).round(2)
    return grouped.sort_values("LossRatio")


def identify_segments(
    segment_df: pd.DataFrame, segment_col: str, top_n: int = 3
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Identify best and worst performing segments by loss ratio."""
    sorted_df = segment_df.sort_values("LossRatio")
    best = sorted_df.head(top_n).copy()
    best["Rank"] = range(1, len(best) + 1)
    worst = sorted_df.tail(top_n).sort_values("LossRatio", ascending=False).copy()
    worst["Rank"] = range(1, len(worst) + 1)
    return best, worst
