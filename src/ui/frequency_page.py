"""Frequency Modeling page."""

import pandas as pd
import streamlit as st

from src.modeling.frequency import fit_frequency_models
from src.utils.session import get_active_data
from src.utils.styling import render_kpi_card, render_section_header


def render() -> None:
    """Render the frequency modeling module."""
    st.title("Frequency Modeling")
    df = get_active_data()

    if df is None:
        st.warning("No data available. Upload and clean data first.")
        return

    if st.button("Fit Frequency Models", type="primary"):
        with st.spinner("Fitting Poisson and Negative Binomial GLMs..."):
            try:
                result = fit_frequency_models(df)
                st.session_state.frequency_result = result
                st.success("Models fitted successfully.")
            except Exception as exc:
                st.error(f"Model fitting failed: {exc}")

    result = st.session_state.get("frequency_result")

    if result is None:
        st.info(
            "Click **Fit Frequency Models** to run Poisson and Negative Binomial GLMs."
        )
        return

    render_section_header("Model Comparison")
    st.dataframe(result.comparison, use_container_width=True)

    preferred = result.preferred_model
    st.success(f"Preferred Model: **{preferred}** (lower AIC)")

    tab_pois, tab_nb = st.tabs(
        ["Poisson GLM", "Negative Binomial GLM"]
    )

    # =====================================================
    # POISSON MODEL
    # =====================================================

    with tab_pois:

        render_section_header("Poisson GLM — Coefficients")

        st.dataframe(
            result.poisson.coefficients,
            use_container_width=True,
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            render_kpi_card(
                "AIC",
                str(result.poisson.aic)
            )

        with c2:
            render_kpi_card(
                "BIC",
                str(result.poisson.bic)
            )

        with c3:
            render_kpi_card(
                "Pseudo R²",
                str(result.poisson.pseudo_r2)
            )

        render_section_header("Model Diagnostics")

        diag = result.poisson.diagnostics

        d1, d2, d3, d4 = st.columns(4)

        with d1:
            render_kpi_card(
                "Converged",
                "Yes" if diag["converged"] else "No"
            )

        with d2:
            render_kpi_card(
                "Pearson χ²",
                f"{diag['pearson_chi2']:,.2f}"
            )

        with d3:
            render_kpi_card(
                "Model DF",
                str(int(diag["df_model"]))
            )

        with d4:
            render_kpi_card(
                "Residual DF",
                str(int(diag["df_resid"]))
            )

        diagnostics_df = pd.DataFrame(
            {
                "Metric": [
                    "AIC",
                    "BIC",
                    "Deviance",
                    "Pseudo R²",
                ],
                "Value": [
                    result.poisson.aic,
                    result.poisson.bic,
                    result.poisson.deviance,
                    result.poisson.pseudo_r2,
                ],
            }
        )

        st.dataframe(
            diagnostics_df,
            use_container_width=True,
            hide_index=True,
        )

    # =====================================================
    # NEGATIVE BINOMIAL MODEL
    # =====================================================

    with tab_nb:

        render_section_header(
            "Negative Binomial GLM — Coefficients"
        )

        st.dataframe(
            result.negative_binomial.coefficients,
            use_container_width=True,
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            render_kpi_card(
                "AIC",
                str(result.negative_binomial.aic)
            )

        with c2:
            render_kpi_card(
                "BIC",
                str(result.negative_binomial.bic)
            )

        with c3:
            render_kpi_card(
                "Pseudo R²",
                str(result.negative_binomial.pseudo_r2)
            )

        render_section_header("Model Diagnostics")

        diag = result.negative_binomial.diagnostics

        d1, d2, d3, d4 = st.columns(4)

        with d1:
            render_kpi_card(
                "Converged",
                "Yes" if diag["converged"] else "No"
            )

        with d2:
            render_kpi_card(
                "Pearson χ²",
                f"{diag['pearson_chi2']:,.2f}"
            )

        with d3:
            render_kpi_card(
                "Model DF",
                str(int(diag["df_model"]))
            )

        with d4:
            render_kpi_card(
                "Residual DF",
                str(int(diag["df_resid"]))
            )

        diagnostics_df = pd.DataFrame(
            {
                "Metric": [
                    "AIC",
                    "BIC",
                    "Deviance",
                    "Pseudo R²",
                ],
                "Value": [
                    result.negative_binomial.aic,
                    result.negative_binomial.bic,
                    result.negative_binomial.deviance,
                    result.negative_binomial.pseudo_r2,
                ],
            }
        )

        st.dataframe(
            diagnostics_df,
            use_container_width=True,
            hide_index=True,
        )