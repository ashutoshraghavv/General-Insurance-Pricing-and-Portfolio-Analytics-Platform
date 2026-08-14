"""Home page."""

import streamlit as st

from src.utils.styling import render_kpi_card, render_section_header


def render() -> None:
    """Render the home / landing page."""
    st.title("Actuarial Pricing & Portfolio Analytics Platform")
    st.markdown(
        """
        End-to-end **General Insurance** actuarial workflow platform covering
        data ingestion through executive reporting.
        """
    )

    render_section_header("Platform Workflow")
    cols = st.columns(3)
    steps = [
        ("1. Upload", "Load CSV/XLSX or sample portfolio data"),
        ("2. Validate", "Run data quality checks and scoring"),
        ("3. Clean", "Treat missing values, duplicates, outliers"),
        ("4. Explore", "Interactive EDA dashboards"),
        ("5. Model", "Frequency & severity GLMs"),
        ("6. Price", "Pure premium estimation"),
        ("7. Analyze", "Portfolio KPIs & segment profitability"),
        ("8. Report", "Executive PDF & Excel exports"),
    ]
    for i, (title, desc) in enumerate(steps):
        with cols[i % 3]:
            st.markdown(f"**{title}**")
            st.caption(desc)

    render_section_header("Quick Status")
    c1, c2, c3, c4 = st.columns(4)
    has_data = st.session_state.get("raw_data") is not None
    has_clean = st.session_state.get("cleaned_data") is not None
    has_models = st.session_state.get("frequency_result") is not None

    with c1:
        render_kpi_card("Data Loaded", "Yes" if has_data else "No")
    with c2:
        render_kpi_card("Data Cleaned", "Yes" if has_clean else "No")
    with c3:
        render_kpi_card("Models Fitted", "Yes" if has_models else "No")
    with c4:
        source = st.session_state.get("data_source") or "None"
        render_kpi_card("Data Source", source)

    st.info("Use the sidebar to navigate through each module. Start with **Data Upload** or load the sample dataset.")
