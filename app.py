"""
Actuarial Pricing & Portfolio Analytics Platform
Main Streamlit application entry point.
"""

import streamlit as st

from src.config import PAGE_OPTIONS
from src.ui import (
    cleaning_page,
    eda_page,
    frequency_page,
    home,
    portfolio_page,
    pure_premium_page,
    reporting_page,
    severity_page,
    upload,
    validation_page,
)
from src.utils.logging_config import setup_logging
from src.utils.session import init_session_state
from src.utils.styling import apply_custom_css

setup_logging()

st.set_page_config(
    page_title="Actuarial Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
init_session_state()

PAGE_MAP = {
    "Home": home.render,
    "Data Upload": upload.render,
    "Validation": validation_page.render,
    "Cleaning": cleaning_page.render,
    "Exploratory Analytics": eda_page.render,
    "Frequency Modeling": frequency_page.render,
    "Severity Modeling": severity_page.render,
    "Pure Premium": pure_premium_page.render,
    "Portfolio Analytics": portfolio_page.render,
    "Executive Reporting": reporting_page.render,
}

with st.sidebar:
    st.markdown("## Actuarial Pricing & Portfolio Analytics Platform")
    st.caption("General Insurance Pricing & Analytics")
    st.divider()
    page = st.radio("Navigation", PAGE_OPTIONS, label_visibility="collapsed")
    st.divider()
    st.caption("v1.0.0 | End-to-End Actuarial Workflow")

PAGE_MAP[page]()
