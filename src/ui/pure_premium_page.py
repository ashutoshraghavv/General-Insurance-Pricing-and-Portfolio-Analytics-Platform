"""Pure Premium page."""

import streamlit as st

from src.pricing.pure_premium import calculate_pure_premium
from src.utils.session import get_active_data
from src.utils.styling import render_kpi_card, render_section_header


def render() -> None:
    """Render the pure premium estimation module."""
    st.title("Pure Premium Estimation")
    df = get_active_data()

    if df is None:
        st.warning("No data available. Upload and clean data first.")
        return

    if st.button("Calculate Pure Premium", type="primary"):
        with st.spinner("Calculating pure premium..."):
            freq = st.session_state.get("frequency_result")
            sev = st.session_state.get("severity_result")
            result = calculate_pure_premium(df, freq, sev)
            st.session_state.pure_premium_result = result
            st.success("Pure premium calculated.")

    result = st.session_state.get("pure_premium_result")
    if result is None:
        st.info("Click **Calculate Pure Premium** to estimate technical premium.")
        return

    render_section_header("Portfolio Pure Premium")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Pure Premium", f"${result.portfolio_pure_premium:,.2f}")
    with c2:
        render_kpi_card("Expected Frequency", f"{result.portfolio_expected_frequency:.4f}")
    with c3:
        render_kpi_card("Expected Severity", f"${result.portfolio_expected_severity:,.0f}")
    with c4:
        render_kpi_card("Models Used", f"{result.frequency_model_used} / {result.severity_model_used}")

    st.markdown(
        f"**Formula:** Pure Premium = Expected Frequency "
        f"* Expected Severity"
        )

    render_section_header("Segment Estimates")
    if not result.segment_estimates.empty:
        segment_type = st.selectbox(
            "Segment Type",
            result.segment_estimates["SegmentType"].unique(),
        )
        filtered = result.segment_estimates[
            result.segment_estimates["SegmentType"] == segment_type
        ]
        st.dataframe(filtered, use_container_width=True)

    render_section_header("Profitability Metrics")
    if not result.profitability.empty:
        st.dataframe(result.profitability, use_container_width=True)

    with st.expander("Policy-Level Estimates (sample)"):
        st.dataframe(result.policy_estimates.head(100), use_container_width=True)
