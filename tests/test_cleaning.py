"""Tests for cleaning engine."""

import pandas as pd
import pytest

from src.cleaning.engine import clean_portfolio
from src.data.generator import generate_sample_portfolio
from src.validation.engine import validate_portfolio


@pytest.fixture
def dirty_df() -> pd.DataFrame:
    """Generate dirty sample data."""
    return generate_sample_portfolio(n_rows=500, seed=42)


def test_cleaning_reduces_issues(dirty_df: pd.DataFrame) -> None:
    """Cleaning should reduce validation issues."""
    before = validate_portfolio(dirty_df)
    result = clean_portfolio(dirty_df)
    after = validate_portfolio(result.cleaned_df)
    assert after.total_issues <= before.total_issues


def test_cleaning_removes_duplicates(dirty_df: pd.DataFrame) -> None:
    """Cleaning should remove duplicate PolicyIDs."""
    result = clean_portfolio(dirty_df)
    assert result.after_metrics["duplicate_policy_ids"] == 0


def test_cleaning_fixes_exposure(dirty_df: pd.DataFrame) -> None:
    """Cleaning should remove invalid exposure rows."""
    result = clean_portfolio(dirty_df)
    assert result.after_metrics["invalid_exposure"] == 0
    assert (result.cleaned_df["Exposure"] > 0).all()


def test_cleaning_actions_recorded(dirty_df: pd.DataFrame) -> None:
    """Cleaning should record actions taken."""
    result = clean_portfolio(dirty_df)
    assert len(result.actions) > 0
    assert result.before_metrics["row_count"] >= result.after_metrics["row_count"]
