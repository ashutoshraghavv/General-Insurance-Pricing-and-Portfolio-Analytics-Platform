"""Exploratory Analytics page."""

import streamlit as st

from src.eda.charts import (
    claim_frequency_chart,
    claim_severity_chart,
    correlation_heatmap,
    distribution_chart,
    monthly_trends_chart,
    segment_analysis_chart,
)
from src.utils.session import get_active_data
from src.utils.styling import render_section_header


def render() -> None:
    """Render the EDA module."""
    st.title("Exploratory Analytics")
    df = get_active_data()

    if df is None:
        st.warning("No data available. Upload and clean data first.")
        return

    render_section_header("Distribution Analysis")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(distribution_chart(df, "Premium", "Premium Distribution"), use_container_width=True)
    with c2:
        st.plotly_chart(distribution_chart(df, "ClaimAmount", "Claim Amount Distribution"), use_container_width=True)
    with c3:
        st.plotly_chart(distribution_chart(df, "Exposure", "Exposure Distribution"), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(claim_frequency_chart(df), use_container_width=True)
    with c2:
        st.plotly_chart(claim_severity_chart(df), use_container_width=True)

    render_section_header("Trends & Correlations")
    st.plotly_chart(monthly_trends_chart(df), use_container_width=True)
    st.plotly_chart(correlation_heatmap(df), use_container_width=True)

    render_section_header("Segment Analysis")
    segment_col = st.selectbox("Segment By", ["ProductLine", "Region", "Channel"])
    metric = st.selectbox("Metric", ["LossRatio", "ClaimFrequency", "AvgSeverity"])
    st.plotly_chart(segment_analysis_chart(df, segment_col, metric), use_container_width=True)
