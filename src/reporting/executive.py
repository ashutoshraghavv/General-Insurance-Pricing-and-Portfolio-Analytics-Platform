"""Executive report generation and export."""

import logging
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Optional

import pandas as pd
from fpdf import FPDF

from src.analytics.portfolio import PortfolioKPIs, segment_profitability

logger = logging.getLogger("actuarial_platform")


@dataclass
class ExecutiveReport:
    """Structured executive report content."""

    portfolio_overview: str
    key_findings: list[str]
    risk_areas: list[str]
    recommendations: list[str]
    kpis: PortfolioKPIs
    generated_at: str


def generate_executive_report(
    df: pd.DataFrame,
    kpis: PortfolioKPIs,
    pure_premium: Optional[float] = None,
    frequency_model: str = "N/A",
    severity_model: str = "N/A",
) -> ExecutiveReport:
    """Generate narrative executive report sections from portfolio data."""
    product_perf = segment_profitability(df, "ProductLine")
    region_perf = segment_profitability(df, "Region")
    channel_perf = segment_profitability(df, "Channel")

    best_product = product_perf.iloc[0]
    worst_product = product_perf.iloc[-1]
    best_region = region_perf.iloc[0]
    worst_region = region_perf.iloc[-1]

    pp = pure_premium or kpis.pure_premium
    rate_adequacy = (kpis.written_premium / (pp * kpis.exposure) * 100) if pp > 0 else 0

    overview = (
        f"The portfolio comprises {kpis.policy_count:,} policies with "
        f"{kpis.exposure:,.1f} total exposure units. Written premium totals "
        f"${kpis.written_premium:,.0f} against ${kpis.total_claims:,.0f} in incurred claims, "
        f"producing a loss ratio of {kpis.loss_ratio:.1f}%. "
        f"Modeled pure premium is ${pp:,.2f} per exposure unit using "
        f"{frequency_model} frequency and {severity_model} severity models."
    )

    findings = [
        f"Portfolio loss ratio stands at {kpis.loss_ratio:.1f}% with claim frequency of "
        f"{kpis.claim_frequency:.4f} and average severity of ${kpis.claim_severity:,.0f}.",
        f"Best performing product line: {best_product['ProductLine']} "
        f"(LR: {best_product['LossRatio']:.1f}%).",
        f"Worst performing product line: {worst_product['ProductLine']} "
        f"(LR: {worst_product['LossRatio']:.1f}%).",
        f"Rate adequacy indicator: {rate_adequacy:.1f}% of indicated pure premium.",
        f"Strongest region: {best_region['Region']} (LR: {best_region['LossRatio']:.1f}%).",
    ]

    risk_areas = []
    high_lr_products = product_perf[product_perf["LossRatio"] > 70]
    for _, row in high_lr_products.iterrows():
        risk_areas.append(
            f"{row['ProductLine']}: Loss ratio {row['LossRatio']:.1f}% exceeds target threshold."
        )

    high_lr_regions = region_perf[region_perf["LossRatio"] > 75]
    for _, row in high_lr_regions.iterrows():
        risk_areas.append(
            f"{row['Region']} region: Elevated loss ratio at {row['LossRatio']:.1f}%."
        )

    worst_channel = channel_perf.iloc[-1]
    risk_areas.append(
        f"{worst_channel['Channel']} channel underperforming with "
        f"{worst_channel['LossRatio']:.1f}% loss ratio."
    )

    if not risk_areas:
        risk_areas.append("No critical risk areas identified above threshold levels.")

    recommendations = []
    if worst_product["LossRatio"] > 65:
        recommendations.append(
            f"Review pricing for {worst_product['ProductLine']} — consider rate increase "
            f"or tighter underwriting criteria."
        )
    if rate_adequacy < 95:
        recommendations.append(
            "Overall rate adequacy below 95% — recommend portfolio-wide rate review."
        )
    if worst_region["LossRatio"] > 70:
        recommendations.append(
            f"Investigate claims experience in {worst_region['Region']} region "
            f"for potential fraud or catastrophe exposure."
        )
    recommendations.append(
        f"Prioritize retention in {best_product['ProductLine']} segment "
        f"which demonstrates favorable profitability."
    )
    recommendations.append(
        "Implement quarterly monitoring of loss ratio trends by segment "
        "to enable proactive pricing adjustments."
    )

    return ExecutiveReport(
        portfolio_overview=overview,
        key_findings=findings,
        risk_areas=risk_areas,
        recommendations=recommendations,
        kpis=kpis,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


def export_to_excel(
    report: ExecutiveReport,
    df: pd.DataFrame,
    segment_data: Optional[pd.DataFrame] = None,
) -> BytesIO:
    """Export executive report and analytics to Excel."""

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

        pd.DataFrame(
            {
                "Metric": list(report.kpis.to_dict().keys()),
                "Value": list(report.kpis.to_dict().values()),
            }
        ).to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False,
        )

        product_analysis = segment_profitability(
            df,
            "ProductLine",
        )

        region_analysis = segment_profitability(
            df,
            "Region",
        )

        channel_analysis = segment_profitability(
            df,
            "Channel",
        )

        product_analysis.to_excel(
            writer,
            sheet_name="Product Analysis",
            index=False,
        )

        region_analysis.to_excel(
            writer,
            sheet_name="Region Analysis",
            index=False,
        )

        channel_analysis.to_excel(
            writer,
            sheet_name="Channel Analysis",
            index=False,
        )

        findings_df = pd.DataFrame(
            {
                "Key Findings": report.key_findings,
            }
        )

        findings_df.to_excel(
            writer,
            sheet_name="Findings",
            index=False,
        )

        risk_df = pd.DataFrame(
            {
                "Risk Areas": report.risk_areas,
            }
        )

        risk_df.to_excel(
            writer,
            sheet_name="Risk Areas",
            index=False,
        )

        rec_df = pd.DataFrame(
            {
                "Recommendations": report.recommendations,
            }
        )

        rec_df.to_excel(
            writer,
            sheet_name="Recommendations",
            index=False,
        )

        if segment_data is not None and not segment_data.empty:
            segment_data.to_excel(
                writer,
                sheet_name="Pure Premium",
                index=False,
            )

    buffer.seek(0)
    return buffer

def _sanitize_pdf_text(text: str) -> str:
    """Replace characters that Helvetica/latin-1 encoding cannot render."""
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def export_to_pdf(
    report: ExecutiveReport,
    df: pd.DataFrame,
) -> BytesIO:
    """Export executive report to PDF."""

    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    pdf.add_page()

    effective_width = pdf.epw

    pdf.set_font(
        "Helvetica",
        "B",
        18,
    )

    pdf.cell(
        0,
        10,
        "Actuarial Portfolio Executive Report",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font(
        "Helvetica",
        "",
        10,
    )

    pdf.cell(
        0,
        8,
        f"Generated: {report.generated_at}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(4)

    pdf.set_font(
        "Helvetica",
        "B",
        14,
    )

    pdf.cell(
        0,
        8,
        "Portfolio KPI Summary",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font(
        "Helvetica",
        "",
        10,
    )

    for key, value in report.kpis.to_dict().items():

        if isinstance(value, float):
            display_value = f"{value:,.2f}"
        else:
            display_value = f"{value:,}"

        pdf.cell(
            0,
            6,
            f"{key}: {display_value}",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(5)

    sections = [
        (
            "Portfolio Overview",
            [report.portfolio_overview],
        ),
        (
            "Key Findings",
            report.key_findings,
        ),
        (
            "Risk Areas",
            report.risk_areas,
        ),
        (
            "Recommendations",
            report.recommendations,
        ),
    ]

    for title, items in sections:

        pdf.set_font(
            "Helvetica",
            "B",
            13,
        )

        pdf.cell(
            0,
            8,
            title,
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        for item in items:
            pdf.multi_cell(
                effective_width,
                6,
                _sanitize_pdf_text(f"• {item}"),
            )

        pdf.ln(2)

    buffer = BytesIO()

    pdf.output(buffer)

    buffer.seek(0)

    return buffer