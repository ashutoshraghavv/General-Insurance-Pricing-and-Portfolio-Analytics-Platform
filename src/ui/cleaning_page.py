"""Cleaning page."""

import streamlit as st

from src.cleaning.engine import clean_portfolio
from src.utils.styling import render_kpi_card, render_section_header


def render() -> None:
    """Render the data cleaning module."""
    st.title("Data Cleaning")
    df = st.session_state.get("raw_data")

    if df is None:
        st.warning("No data loaded. Go to **Data Upload** first.")
        return

    if st.button("Run Cleaning Pipeline", type="primary"):
        with st.spinner("Cleaning data..."):
            result = clean_portfolio(df)
            st.session_state.cleaning_result = result
            st.session_state.cleaned_data = result.cleaned_df
            st.success(f"Cleaning complete. {result.rows_removed} rows removed.")

    result = st.session_state.get("cleaning_result")
    if result is None:
        st.info("Click **Run Cleaning Pipeline** to clean the data.")
        return

    render_section_header("Before vs After Metrics")
    c1, c2 = st.columns(2)

    metrics = [
        ("Row Count", "row_count"),
        ("Missing Values", "missing_total"),
        ("Duplicate PolicyIDs", "duplicate_policy_ids"),
        ("Negative Premiums", "negative_premiums"),
        ("Invalid Exposure", "invalid_exposure"),
    ]

    with c1:
        st.markdown("**Before Cleaning**")
        for label, key in metrics:
            render_kpi_card(label, str(result.before_metrics.get(key, "N/A")))

    with c2:
        st.markdown("**After Cleaning**")
        for label, key in metrics:
            render_kpi_card(label, str(result.after_metrics.get(key, "N/A")))

    render_section_header("Cleaning Actions")
    for action in result.actions:
        st.markdown(f"- {action}")

    outlier_count = int(result.outlier_flags.sum()) if len(result.outlier_flags) else 0
    if outlier_count:
        st.warning(f"{outlier_count} outlier records flagged (retained in dataset).")

    with st.expander("Cleaned Data Preview"):
        st.dataframe(result.cleaned_df.head(100), use_container_width=True)
