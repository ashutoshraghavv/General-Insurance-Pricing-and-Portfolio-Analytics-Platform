"""Pure premium calculation engine."""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.modeling.frequency import FrequencyModelResult, predict_frequency
from src.modeling.severity import SeverityComparisonResult

logger = logging.getLogger("actuarial_platform")


@dataclass
class PurePremiumResult:
    """Pure premium estimation results."""

    portfolio_pure_premium: float
    portfolio_expected_frequency: float
    portfolio_expected_severity: float
    segment_estimates: pd.DataFrame
    policy_estimates: pd.DataFrame
    profitability: pd.DataFrame
    frequency_model_used: str
    severity_model_used: str


def _empirical_frequency(df: pd.DataFrame) -> float:
    """Calculate empirical claim frequency."""
    total_claims = df["ClaimCount"].sum()
    total_exposure = df["Exposure"].sum()
    return total_claims / total_exposure if total_exposure > 0 else 0.0


def _empirical_severity(df: pd.DataFrame) -> float:
    """Calculate empirical average severity."""
    claims = df[df["ClaimCount"] > 0]
    if len(claims) == 0:
        return 0.0
    return claims["ClaimAmount"].sum() / claims["ClaimCount"].sum()


def calculate_pure_premium(
    df: pd.DataFrame,
    frequency_result: FrequencyModelResult | None = None,
    severity_result: SeverityComparisonResult | None = None,
) -> PurePremiumResult:
    """
    Calculate pure premium as Expected Frequency × Expected Severity.

    Uses fitted models when available, falls back to empirical estimates.
    """
    data = df.copy()

    if frequency_result:
        preferred = (
            frequency_result.negative_binomial
            if frequency_result.preferred_model == "Negative Binomial"
            else frequency_result.poisson
        )
        try:
            freq_rates = predict_frequency(preferred, data)
            data["ExpectedFrequency"] = freq_rates
            portfolio_freq = float(np.average(freq_rates, weights=data["Exposure"]))
            freq_model = frequency_result.preferred_model
        except Exception:
            portfolio_freq = _empirical_frequency(data)
            data["ExpectedFrequency"] = portfolio_freq
            freq_model = "Empirical"
    else:
        portfolio_freq = _empirical_frequency(data)
        data["ExpectedFrequency"] = portfolio_freq
        freq_model = "Empirical"

    if severity_result:
        if severity_result.preferred_model == "Gamma":
            portfolio_sev = severity_result.gamma.expected_severity
        else:
            portfolio_sev = severity_result.lognormal.expected_severity
        sev_model = severity_result.preferred_model
    else:
        portfolio_sev = _empirical_severity(data)
        sev_model = "Empirical"

    data["ExpectedSeverity"] = portfolio_sev
    data["PurePremium"] = data["ExpectedFrequency"] * data["ExpectedSeverity"]
    data["RateAdequacy"] = np.where(
        data["PurePremium"] > 0,
        data["Premium"] / data["PurePremium"],
        np.nan,
    )

    portfolio_pp = portfolio_freq * portfolio_sev

    segment_cols = ["ProductLine", "Region", "Channel"]
    segment_frames = []
    for col in segment_cols:
        if col not in data.columns:
            continue
        seg = (
            data.groupby(col)
            .agg(
                Exposure=("Exposure", "sum"),
                ExpectedFrequency=("ExpectedFrequency", "mean"),
                ExpectedSeverity=("ExpectedSeverity", "first"),
                PurePremium=("PurePremium", "mean"),
                WrittenPremium=("Premium", "sum"),
                TotalClaims=("ClaimAmount", "sum"),
                PolicyCount=("PolicyID", "count"),
            )
            .reset_index()
        )
        seg["SegmentType"] = col
        seg.rename(columns={col: "Segment"}, inplace=True)
        seg["LossRatio"] = (seg["TotalClaims"] / seg["WrittenPremium"] * 100).round(2)
        seg["CombinedRatio"] = seg["LossRatio"]
        segment_frames.append(seg)

    segment_estimates = pd.concat(segment_frames, ignore_index=True) if segment_frames else pd.DataFrame()

    profitability = segment_estimates.copy()
    if not profitability.empty:
        profitability["ProfitMargin"] = (
            (profitability["WrittenPremium"] - profitability["TotalClaims"])
            / profitability["WrittenPremium"]
            * 100
        ).round(2)

    logger.info(
        "Pure premium: freq=%.4f, sev=%.2f, PP=%.2f",
        portfolio_freq,
        portfolio_sev,
        portfolio_pp,
    )

    return PurePremiumResult(
        portfolio_pure_premium=round(portfolio_pp, 2),
        portfolio_expected_frequency=round(portfolio_freq, 6),
        portfolio_expected_severity=round(portfolio_sev, 2),
        segment_estimates=segment_estimates,
        policy_estimates=data[
            [
                "PolicyID",
                "ProductLine",
                "Region",
                "Channel",
                "Exposure",
                "Premium",
                "ExpectedFrequency",
                "ExpectedSeverity",
                "PurePremium",
                "RateAdequacy",
            ]
        ],
        profitability=profitability,
        frequency_model_used=freq_model,
        severity_model_used=sev_model,
    )
