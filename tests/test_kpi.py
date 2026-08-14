"""Tests for KPI calculations."""

import pandas as pd
import pytest

from src.analytics.portfolio import calculate_kpis, segment_profitability
from src.data.generator import generate_sample_portfolio


@pytest.fixture
def clean_df() -> pd.DataFrame:
    """Generate and clean sample data."""
    from src.cleaning.engine import clean_portfolio

    return clean_portfolio(generate_sample_portfolio(n_rows=500, seed=42)).cleaned_df


def test_kpi_calculation(clean_df: pd.DataFrame) -> None:
    """KPIs should be calculated with valid values."""
    kpis = calculate_kpis(clean_df)
    assert kpis.policy_count == len(clean_df)
    assert kpis.written_premium > 0
    assert kpis.exposure > 0
    assert kpis.loss_ratio >= 0


def test_kpi_loss_ratio(clean_df: pd.DataFrame) -> None:
    """Loss ratio should equal claims / premium * 100."""
    kpis = calculate_kpis(clean_df)
    expected = clean_df["ClaimAmount"].sum() / clean_df["Premium"].sum() * 100
    assert abs(kpis.loss_ratio - round(expected, 2)) < 0.1


def test_kpi_claim_frequency(clean_df: pd.DataFrame) -> None:
    """Claim frequency should equal total claims / exposure."""
    kpis = calculate_kpis(clean_df)
    expected = clean_df["ClaimCount"].sum() / clean_df["Exposure"].sum()
    assert abs(kpis.claim_frequency - round(expected, 6)) < 0.0001


def test_segment_profitability(clean_df: pd.DataFrame) -> None:
    """Segment profitability should return grouped metrics."""
    seg = segment_profitability(clean_df, "ProductLine")
    assert len(seg) == clean_df["ProductLine"].nunique()
    assert "LossRatio" in seg.columns
    assert "ProfitMargin" in seg.columns
