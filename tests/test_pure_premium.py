"""Tests for pure premium calculations."""

import pandas as pd
import pytest

from src.cleaning.engine import clean_portfolio
from src.data.generator import generate_sample_portfolio
from src.modeling.frequency import fit_frequency_models
from src.modeling.severity import fit_severity_models
from src.pricing.pure_premium import calculate_pure_premium


@pytest.fixture
def model_df() -> pd.DataFrame:
    """Generate cleaned data for modeling."""
    return clean_portfolio(generate_sample_portfolio(n_rows=1000, seed=42)).cleaned_df


def test_pure_premium_empirical(model_df: pd.DataFrame) -> None:
    """Pure premium should calculate without models."""
    result = calculate_pure_premium(model_df)
    assert result.portfolio_pure_premium > 0
    assert result.portfolio_expected_frequency > 0
    assert result.portfolio_expected_severity > 0
    assert result.portfolio_pure_premium == pytest.approx(
        result.portfolio_expected_frequency * result.portfolio_expected_severity,
        rel=0.01,
    )


def test_pure_premium_with_models(model_df: pd.DataFrame) -> None:
    """Pure premium should use fitted models when available."""
    freq = fit_frequency_models(model_df)
    sev = fit_severity_models(model_df)
    result = calculate_pure_premium(model_df, freq, sev)
    assert result.portfolio_pure_premium > 0
    assert result.frequency_model_used in ("Poisson", "Negative Binomial")
    assert result.severity_model_used in ("Gamma", "Lognormal")
    assert not result.segment_estimates.empty


def test_pure_premium_policy_estimates(model_df: pd.DataFrame) -> None:
    """Policy-level estimates should be generated for all policies."""
    result = calculate_pure_premium(model_df)
    assert len(result.policy_estimates) == len(model_df)
    assert "PurePremium" in result.policy_estimates.columns
    assert "RateAdequacy" in result.policy_estimates.columns
