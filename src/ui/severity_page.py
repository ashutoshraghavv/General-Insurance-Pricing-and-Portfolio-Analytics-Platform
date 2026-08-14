"""Severity Modeling page."""

import streamlit as st

from src.modeling.severity import fit_severity_models
from src.utils.session import get_active_data
from src.utils.styling import render_kpi_card, render_section_header


def render() -> None:
    """Render the severity modeling module."""
    st.title("Severity Modeling")
    df = get_active_data()

    if df is None:
        st.warning("No data available. Upload and clean data first.")
        return

    if st.button("Fit Severity Models", type="primary"):
        with st.spinner("Fitting Gamma and Lognormal models..."):
            try:
                result = fit_severity_models(df)
                st.session_state.severity_result = result
                st.success("Severity models fitted successfully.")
            except Exception as exc:
                st.error(f"Model fitting failed: {exc}")

    result = st.session_state.get("severity_result")
    if result is None:
        st.info("Click **Fit Severity Models** to run Gamma and Lognormal fits.")
        return

    render_section_header("Model Comparison")
    st.dataframe(result.comparison, use_container_width=True)
    st.success(f"Preferred Model: **{result.preferred_model}** (lower AIC)")

    tab_gamma, tab_logn = st.tabs(["Gamma Model", "Lognormal Model"])

    with tab_gamma:
        render_section_header("Gamma — Fitted Parameters")
        for param, value in result.gamma.parameters.items():
            render_kpi_card(param, str(value))
        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Expected Severity", f"${result.gamma.expected_severity:,.0f}")
        with c2:
            render_kpi_card("AIC", str(result.gamma.aic))
        with c3:
            render_kpi_card("Goodness of Fit", result.gamma.goodness_of_fit)
        st.caption(f"KS statistic: {result.gamma.ks_statistic}, p-value: {result.gamma.ks_pvalue}")

    with tab_logn:
        render_section_header("Lognormal — Fitted Parameters")
        for param, value in result.lognormal.parameters.items():
            render_kpi_card(param, str(value))
        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Expected Severity", f"${result.lognormal.expected_severity:,.0f}")
        with c2:
            render_kpi_card("AIC", str(result.lognormal.aic))
        with c3:
            render_kpi_card("Goodness of Fit", result.lognormal.goodness_of_fit)
        st.caption(f"KS statistic: {result.lognormal.ks_statistic}, p-value: {result.lognormal.ks_pvalue}")
