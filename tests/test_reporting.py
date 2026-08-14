"""Tests for executive report exports."""

from src.analytics.portfolio import calculate_kpis
from src.cleaning.engine import clean_portfolio
from src.data.generator import generate_sample_portfolio
from src.reporting.executive import export_to_excel, export_to_pdf, generate_executive_report


def test_pdf_export() -> None:
    """PDF export should produce non-empty bytes."""
    df = clean_portfolio(generate_sample_portfolio(n_rows=500, seed=42)).cleaned_df
    kpis = calculate_kpis(df)
    report = generate_executive_report(df, kpis)
    pdf = export_to_pdf(report)
    assert len(pdf.getvalue()) > 500


def test_excel_export() -> None:
    """Excel export should produce non-empty bytes."""
    df = clean_portfolio(generate_sample_portfolio(n_rows=500, seed=42)).cleaned_df
    kpis = calculate_kpis(df)
    report = generate_executive_report(df, kpis)
    xlsx = export_to_excel(report, df)
    assert len(xlsx.getvalue()) > 1000
