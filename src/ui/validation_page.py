"""Validation page."""

import streamlit as st

from src.validation.engine import validate_portfolio
from src.utils.styling import render_kpi_card, render_pass_fail, render_section_header


def render() -> None:
    """Render the validation module."""
    st.title("Data Validation")
    df = st.session_state.get("raw_data")

    if df is None:
        st.warning("No data loaded. Go to **Data Upload** first.")
        return

    if st.button("Run Validation", type="primary"):
        with st.spinner("Running validation checks..."):
            result = validate_portfolio(df)
            st.session_state.validation_result = result

    result = st.session_state.get("validation_result")
    if result is None:
        st.info("Click **Run Validation** to execute data quality checks.")
        return

    render_section_header("Validation Results")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Validation Score", f"{result.score}%")
    with c2:
        render_kpi_card("Total Issues", str(result.total_issues))
    with c3:
        st.markdown("**Status**")
        render_pass_fail(result.passed)

    if not result.issue_summary.empty:
        render_section_header("Issue Summary")
        st.dataframe(result.issue_summary, use_container_width=True)

        render_section_header("Issue Details")
        for issue in result.issues:
            with st.expander(f"{issue.rule} — {issue.count} records ({issue.severity})"):
                st.write(issue.description)
                if not issue.affected_rows.empty:
                    st.dataframe(issue.affected_rows, use_container_width=True)
    else:
        st.success("No validation issues found.")
