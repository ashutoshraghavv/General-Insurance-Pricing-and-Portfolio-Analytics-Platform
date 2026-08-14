"""Streamlit UI styling utilities."""

import streamlit as st


def apply_custom_css() -> None:
    """Apply Actuarial Power BI-inspired styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f2b46 0%, #1a3a5c 100%);
        }

        [data-testid="stSidebar"] * {
            color: #e8eef4 !important;
        }

        [data-testid="stSidebar"] .stRadio label {
            font-size: 0.95rem;
            padding: 0.35rem 0;
        }

        .kpi-card {
            background: linear-gradient(135deg, #ffffff 0%, #f4f7fb 100%);
            border: 1px solid #d9e2ec;
            border-left: 4px solid #0078d4;
            border-radius: 8px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 2px 8px rgba(15, 43, 70, 0.08);
            min-height: 100px;
        }

        .kpi-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #5a6a7a;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
        }

        .kpi-value {
            font-size: 1.65rem;
            font-weight: 700;
            color: #0f2b46;
            line-height: 1.2;
        }

        .kpi-delta {
            font-size: 0.82rem;
            color: #0078d4;
            margin-top: 0.25rem;
        }

        .section-header {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f2b46;
            border-bottom: 2px solid #0078d4;
            padding-bottom: 0.4rem;
            margin-bottom: 1rem;
        }

        .pass-badge {
            background: #dff6dd;
            color: #107c10;
            padding: 0.35rem 0.75rem;
            border-radius: 4px;
            font-weight: 600;
            display: inline-block;
        }

        .fail-badge {
            background: #fde7e9;
            color: #a80000;
            padding: 0.35rem 0.75rem;
            border-radius: 4px;
            font-weight: 600;
            display: inline-block;
        }

        div[data-testid="stMetric"] {
            background: #f4f7fb;
            border: 1px solid #d9e2ec;
            border-radius: 8px;
            padding: 0.75rem 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, delta: str = "") -> None:
    """Render a styled KPI card."""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str) -> None:
    """Render a section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def render_pass_fail(passed: bool) -> None:
    """Render pass/fail badge."""
    badge_class = "pass-badge" if passed else "fail-badge"
    text = "PASS" if passed else "FAIL"
    st.markdown(f'<span class="{badge_class}">{text}</span>', unsafe_allow_html=True)
