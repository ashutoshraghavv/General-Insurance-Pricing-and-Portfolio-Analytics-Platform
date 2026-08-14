"""Severity modeling: Gamma and Lognormal distributions."""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger("actuarial_platform")


@dataclass
class SeverityModelResult:
    """Result for a single severity distribution fit."""

    name: str
    parameters: dict[str, float]
    expected_severity: float
    aic: float
    ks_statistic: float
    ks_pvalue: float
    goodness_of_fit: str


@dataclass
class SeverityComparisonResult:
    """Comparison of Gamma vs Lognormal severity models."""

    gamma: SeverityModelResult
    lognormal: SeverityModelResult
    preferred_model: str
    comparison: pd.DataFrame


def _get_severity_data(df: pd.DataFrame) -> np.ndarray:
    """Extract per-claim severity values from policies with claims."""
    claims = df[df["ClaimCount"] > 0].copy()
    claims["Severity"] = claims["ClaimAmount"] / claims["ClaimCount"]
    severity = claims["Severity"].values
    severity = severity[severity > 0]
    return severity


def _fit_gamma(severity: np.ndarray) -> SeverityModelResult:
    """Fit Gamma distribution to severity data."""
    alpha, loc, scale = stats.gamma.fit(severity, floc=0)
    expected = alpha * scale
    log_likelihood = np.sum(stats.gamma.logpdf(severity, alpha, loc=loc, scale=scale))
    aic = 2 * 2 - 2 * log_likelihood
    ks_stat, ks_p = stats.kstest(
        severity, lambda x: stats.gamma.cdf(x, alpha, loc=loc, scale=scale)
    )
    gof = "Good" if ks_p > 0.05 else "Moderate" if ks_p > 0.01 else "Poor"

    return SeverityModelResult(
        name="Gamma",
        parameters={"alpha (shape)": round(alpha, 4), "scale": round(scale, 4)},
        expected_severity=round(expected, 2),
        aic=round(aic, 2),
        ks_statistic=round(ks_stat, 4),
        ks_pvalue=round(ks_p, 4),
        goodness_of_fit=gof,
    )


def _fit_lognormal(severity: np.ndarray) -> SeverityModelResult:
    """Fit Lognormal distribution to severity data."""
    shape, loc, scale = stats.lognorm.fit(severity, floc=0)
    expected = np.exp(np.log(scale) + 0.5 * shape**2)
    log_likelihood = np.sum(stats.lognorm.logpdf(severity, shape, loc=loc, scale=scale))
    aic = 2 * 2 - 2 * log_likelihood
    ks_stat, ks_p = stats.kstest(
        severity, lambda x: stats.lognorm.cdf(x, shape, loc=loc, scale=scale)
    )
    gof = "Good" if ks_p > 0.05 else "Moderate" if ks_p > 0.01 else "Poor"

    return SeverityModelResult(
        name="Lognormal",
        parameters={"sigma (shape)": round(shape, 4), "scale": round(scale, 4)},
        expected_severity=round(expected, 2),
        aic=round(aic, 2),
        ks_statistic=round(ks_stat, 4),
        ks_pvalue=round(ks_p, 4),
        goodness_of_fit=gof,
    )


def fit_severity_models(df: pd.DataFrame) -> SeverityComparisonResult:
    """Fit and compare Gamma and Lognormal severity models."""
    severity = _get_severity_data(df)
    if len(severity) < 10:
        raise ValueError("Insufficient claim data for severity modeling (need >= 10 claims)")

    gamma = _fit_gamma(severity)
    lognormal = _fit_lognormal(severity)

    preferred = "Gamma" if gamma.aic < lognormal.aic else "Lognormal"

    comparison = pd.DataFrame(
        [
            {
                "Model": "Gamma",
                "AIC": gamma.aic,
                "Expected Severity": gamma.expected_severity,
                "KS p-value": gamma.ks_pvalue,
                "Goodness of Fit": gamma.goodness_of_fit,
            },
            {
                "Model": "Lognormal",
                "AIC": lognormal.aic,
                "Expected Severity": lognormal.expected_severity,
                "KS p-value": lognormal.ks_pvalue,
                "Goodness of Fit": lognormal.goodness_of_fit,
            },
        ]
    )

    logger.info(
        "Severity models fitted: Gamma AIC=%.2f, Lognormal AIC=%.2f, preferred=%s",
        gamma.aic,
        lognormal.aic,
        preferred,
    )

    return SeverityComparisonResult(
        gamma=gamma,
        lognormal=lognormal,
        preferred_model=preferred,
        comparison=comparison,
    )
