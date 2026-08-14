"""Streamlit session state helpers."""

from typing import Any, Optional

import pandas as pd
import streamlit as st


def init_session_state() -> None:
    """Initialize default session state keys."""
    defaults: dict[str, Any] = {
        "raw_data": None,
        "cleaned_data": None,
        "validation_result": None,
        "cleaning_result": None,
        "frequency_result": None,
        "severity_result": None,
        "pure_premium_result": None,
        "data_source": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_active_data() -> Optional[pd.DataFrame]:
    """Return cleaned data if available, otherwise raw data."""
    cleaned = st.session_state.get("cleaned_data")
    if cleaned is not None and not cleaned.empty:
        return cleaned
    raw = st.session_state.get("raw_data")
    if raw is not None and not raw.empty:
        return raw
    return None
