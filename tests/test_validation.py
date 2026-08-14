"""Tests for validation engine."""

import pandas as pd
import pytest

from src.data.generator import generate_sample_portfolio
from src.validation.engine import validate_portfolio


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Generate sample portfolio for testing."""
    return generate_sample_portfolio(n_rows=500, seed=42)


def test_validation_detects_issues(sample_df: pd.DataFrame) -> None:
    """Validation should detect injected data quality issues."""
    result = validate_portfolio(sample_df)
    assert result.total_issues > 0
    assert result.score < 100
    assert len(result.issues) > 0


def test_validation_issue_summary(sample_df: pd.DataFrame) -> None:
    """Issue summary should contain rule details."""
    result = validate_portfolio(sample_df)
    assert not result.issue_summary.empty
    assert "Rule" in result.issue_summary.columns
    assert "Count" in result.issue_summary.columns


def test_validation_clean_data_passes() -> None:
    """Clean synthetic data should pass validation."""
    df = pd.DataFrame(
        {
            "PolicyID": ["POL-1", "POL-2"],
            "CustomerID": ["C1", "C2"],
            "ProductLine": ["Motor", "Home"],
            "Region": ["North", "South"],
            "Channel": ["Agent", "Direct"],
            "PolicyStartDate": pd.to_datetime(["2023-01-01", "2023-02-01"]),
            "PolicyEndDate": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "Exposure": [1.0, 0.5],
            "Premium": [1000.0, 500.0],
            "ClaimCount": [0, 1],
            "ClaimAmount": [0.0, 2000.0],
            "Age": [35, 45],
            "VehicleAge": [3, 10],
        }
    )
    result = validate_portfolio(df)
    assert result.total_issues == 0
    assert result.score == 100.0
    assert result.passed is True
