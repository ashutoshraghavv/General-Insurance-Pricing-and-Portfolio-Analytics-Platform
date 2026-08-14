"""Portfolio Analytics page."""

import streamlit as st

from src.analytics.portfolio import calculate_kpis, identify_segments, segment_profitability
from src.utils.session import get_active_data
from src.utils.styling import render_kpi_card, render_section_header


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def render() -> None:
    """Render the portfolio analytics module."""
    st.title("Portfolio Analytics")
    df = get_active_data()

    if df is None:
        st.warning("No data available. Upload and clean data first.")
        return

    pp_result = st.session_state.get("pure_premium_result")
    pure_premium = pp_result.portfolio_pure_premium if pp_result else None
    kpis = calculate_kpis(df, pure_premium)

    render_section_header("Portfolio KPIs")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Written Premium", _format_currency(kpis.written_premium))
    with c2:
        render_kpi_card("Total Claims", _format_currency(kpis.total_claims))
    with c3:
        render_kpi_card("Loss Ratio", f"{kpis.loss_ratio:.1f}%")
    with c4:
        render_kpi_card("Policy Count", f"{kpis.policy_count:,}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Claim Frequency", f"{kpis.claim_frequency:.4f}")
    with c2:
        render_kpi_card("Claim Severity", _format_currency(kpis.claim_severity))
    with c3:
        render_kpi_card("Pure Premium", _format_currency(kpis.pure_premium))
    with c4:
        render_kpi_card("Exposure", f"{kpis.exposure:,.1f}")

    render_section_header("Profitability by Segment")
    segment_col = st.selectbox("Analyze By", ["ProductLine", "Region", "Channel"], key="portfolio_segment")
    seg_df = segment_profitability(df, segment_col, pure_premium)
    st.dataframe(seg_df, use_container_width=True)

    best, worst = identify_segments(seg_df, segment_col)
    c1, c2 = st.columns(2)
    with c1:
        render_section_header("Best Performing Segments")
        st.dataframe(best, use_container_width=True)
    with c2:
        render_section_header("Worst Performing Segments")
        st.dataframe(worst, use_container_width=True)
