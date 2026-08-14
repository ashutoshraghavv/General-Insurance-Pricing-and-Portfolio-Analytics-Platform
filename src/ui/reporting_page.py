import streamlit as st

from src.analytics.portfolio import calculate_kpis
from src.analytics.reporting_charts import (
    loss_ratio_chart,
    premium_claims_chart,
)
from src.reporting.executive import (
    export_to_excel,
    export_to_pdf,
    generate_executive_report,
)
from src.utils.session import get_active_data
from src.utils.styling import (
    render_kpi_card,
    render_section_header,
)


def render() -> None:

    st.title("Executive Reporting")

    df = get_active_data()

    if df is None:
        st.warning("No data available.")
        return

    pp_result = st.session_state.get("pure_premium_result")
    freq_result = st.session_state.get("frequency_result")
    sev_result = st.session_state.get("severity_result")

    pure_premium = (
        pp_result.portfolio_pure_premium
        if pp_result
        else None
    )

    freq_model = (
        freq_result.preferred_model
        if freq_result
        else "Empirical"
    )

    sev_model = (
        sev_result.preferred_model
        if sev_result
        else "Empirical"
    )

    kpis = calculate_kpis(
        df,
        pure_premium,
    )

    report = generate_executive_report(
        df,
        kpis,
        pure_premium,
        freq_model,
        sev_model,
    )

    render_section_header("Portfolio KPIs")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_kpi_card(
            "Written Premium",
            f"${kpis.written_premium:,.0f}",
        )

    with c2:
        render_kpi_card(
            "Total Claims",
            f"${kpis.total_claims:,.0f}",
        )

    with c3:
        render_kpi_card(
            "Loss Ratio",
            f"{kpis.loss_ratio:.1f}%",
        )

    with c4:
        render_kpi_card(
            "Pure Premium",
            f"${kpis.pure_premium:,.0f}",
        )

    st.divider()

    render_section_header("Portfolio Overview")

    st.info(report.portfolio_overview)

    col1, col2 = st.columns(2)

    with col1:

        render_section_header("Key Findings")

        for finding in report.key_findings:
            st.success(finding)

    with col2:

        render_section_header("Risk Areas")

        for risk in report.risk_areas:
            st.warning(risk)

    render_section_header("Recommendations")

    for rec in report.recommendations:
        st.markdown(f"✅ {rec}")

    st.divider()

    render_section_header("Portfolio Analytics")

    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(
            loss_ratio_chart(df, "ProductLine"),
            use_container_width=True,
        )

    with c2:
        st.plotly_chart(
            loss_ratio_chart(df, "Region"),
            use_container_width=True,
        )

    st.plotly_chart(
        premium_claims_chart(df),
        use_container_width=True,
    )

    st.divider()
