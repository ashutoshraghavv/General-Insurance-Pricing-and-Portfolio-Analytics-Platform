"""Portfolio data validation engine."""

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.config import REQUIRED_COLUMNS

logger = logging.getLogger("actuarial_platform")


@dataclass
class ValidationIssue:
    """Single validation issue record."""

    rule: str
    severity: str
    count: int
    description: str
    affected_rows: pd.DataFrame = field(default_factory=pd.DataFrame)


@dataclass
class ValidationResult:
    """Aggregated validation outcome."""

    passed: bool
    score: float
    total_issues: int
    issues: list[ValidationIssue]
    issue_summary: pd.DataFrame

    def to_dict(self) -> dict[str, Any]:
        """Serialize key metrics."""
        return {
            "passed": self.passed,
            "score": self.score,
            "total_issues": self.total_issues,
        }


def _issue(
    rule: str,
    severity: str,
    mask: pd.Series,
    df: pd.DataFrame,
    description: str,
) -> ValidationIssue | None:
    """Build a ValidationIssue from a boolean mask."""
    count = int(mask.sum())
    if count == 0:
        return None
    affected = df.loc[mask].head(50).copy()
    return ValidationIssue(
        rule=rule,
        severity=severity,
        count=count,
        description=description,
        affected_rows=affected,
    )


def validate_portfolio(df: pd.DataFrame) -> ValidationResult:
    """
    Run full validation suite on portfolio data.

    Checks: missing values, duplicate PolicyID, negative premiums,
    negative claim amounts, exposure <= 0, invalid date ranges,
    negative claim counts, missing required columns.
    """
    issues: list[ValidationIssue] = []
    n = len(df)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        issues.append(
            ValidationIssue(
                rule="missing_columns",
                severity="critical",
                count=len(missing_cols),
                description=f"Missing required columns: {', '.join(missing_cols)}",
            )
        )

    if "PolicyID" in df.columns:
        dup_mask = df.duplicated(subset=["PolicyID"], keep=False)
        issue = _issue(
            "duplicate_policy_id",
            "high",
            dup_mask,
            df,
            "Duplicate PolicyID values detected",
        )
        if issue:
            issues.append(issue)

    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            miss_mask = df[col].isna()
            issue = _issue(
                f"missing_{col.lower()}",
                "medium",
                miss_mask,
                df,
                f"Missing values in {col}",
            )
            if issue:
                issues.append(issue)

    if "Premium" in df.columns:
        neg_prem = df["Premium"] < 0
        issue = _issue("negative_premium", "high", neg_prem, df, "Negative premium values")
        if issue:
            issues.append(issue)

    if "ClaimAmount" in df.columns:
        neg_claim = df["ClaimAmount"] < 0
        issue = _issue(
            "negative_claim_amount", "high", neg_claim, df, "Negative claim amounts"
        )
        if issue:
            issues.append(issue)

    if "Exposure" in df.columns:
        bad_exp = df["Exposure"] <= 0
        issue = _issue(
            "invalid_exposure", "high", bad_exp, df, "Exposure <= 0"
        )
        if issue:
            issues.append(issue)

    if "PolicyStartDate" in df.columns and "PolicyEndDate" in df.columns:
        start = pd.to_datetime(df["PolicyStartDate"], errors="coerce")
        end = pd.to_datetime(df["PolicyEndDate"], errors="coerce")
        bad_dates = end < start
        issue = _issue(
            "invalid_date_range",
            "high",
            bad_dates,
            df,
            "Policy end date before start date",
        )
        if issue:
            issues.append(issue)

    if "ClaimCount" in df.columns:
        neg_count = df["ClaimCount"] < 0
        issue = _issue(
            "negative_claim_count", "high", neg_count, df, "Negative claim counts"
        )
        if issue:
            issues.append(issue)

    total_issue_records = sum(i.count for i in issues)
    max_penalty = max(n, 1) * 8
    score = max(0.0, 100.0 - (total_issue_records / max_penalty) * 100)
    score = round(min(score, 100.0), 1)

    critical = any(i.severity == "critical" for i in issues)
    high_count = sum(i.count for i in issues if i.severity in ("critical", "high"))
    passed = not critical and high_count == 0 and score >= 80

    summary = pd.DataFrame(
        [
            {
                "Rule": i.rule,
                "Severity": i.severity,
                "Count": i.count,
                "Description": i.description,
            }
            for i in issues
        ]
    )

    logger.info(
        "Validation complete: score=%.1f, issues=%d, passed=%s",
        score,
        total_issue_records,
        passed,
    )

    return ValidationResult(
        passed=passed,
        score=score,
        total_issues=total_issue_records,
        issues=issues,
        issue_summary=summary,
    )
