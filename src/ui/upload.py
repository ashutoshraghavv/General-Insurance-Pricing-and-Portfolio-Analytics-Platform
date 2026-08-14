"""Data Upload page."""

import streamlit as st

from src.data.loader import (
    get_missing_summary,
    get_schema_summary,
    load_sample_dataset,
    load_uploaded_file,
    validate_required_columns,
)
from src.utils.styling import render_kpi_card, render_section_header


def render() -> None:
    """Render the data upload module."""
    st.title("Data Upload")
    render_section_header("Load Portfolio Data")

    tab_csv, tab_xlsx, tab_sample = st.tabs(["CSV Upload", "XLSX Upload", "Sample Dataset"])

    with tab_csv:
        csv_file = st.file_uploader("Upload CSV file", type=["csv"], key="csv_upload")
        if csv_file is not None:
            try:
                df = load_uploaded_file(csv_file, "csv")
                st.session_state.raw_data = df
                st.session_state.cleaned_data = None
                st.session_state.data_source = csv_file.name
                st.success(f"Loaded {len(df):,} rows from {csv_file.name}")
            except Exception as exc:
                st.error(f"Failed to load CSV: {exc}")

    with tab_xlsx:
        xlsx_file = st.file_uploader("Upload XLSX file", type=["xlsx"], key="xlsx_upload")
        if xlsx_file is not None:
            try:
                df = load_uploaded_file(xlsx_file, "xlsx")
                st.session_state.raw_data = df
                st.session_state.cleaned_data = None
                st.session_state.data_source = xlsx_file.name
                st.success(f"Loaded {len(df):,} rows from {xlsx_file.name}")
            except Exception as exc:
                st.error(f"Failed to load XLSX: {exc}")

    with tab_sample:
        if st.button("Load Sample Portfolio Dataset", type="primary"):
            try:
                df = load_sample_dataset()
                st.session_state.raw_data = df
                st.session_state.cleaned_data = None
                st.session_state.data_source = "Sample Portfolio"
                st.success(f"Loaded sample dataset with {len(df):,} rows")
            except Exception as exc:
                st.error(f"Failed to load sample data: {exc}")

    df = st.session_state.get("raw_data")
    if df is None:
        st.warning("No data loaded. Upload a file or load the sample dataset.")
        return

    render_section_header("Dataset Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Rows", f"{len(df):,}")
    with c2:
        render_kpi_card("Columns", str(len(df.columns)))
    with c3:
        render_kpi_card("Missing Cells", f"{df.isna().sum().sum():,}")

    valid, missing_cols = validate_required_columns(df)
    if not valid:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
    else:
        st.success("All required columns present")

    with st.expander("Schema Preview", expanded=True):
        st.dataframe(get_schema_summary(df), use_container_width=True)

    with st.expander("Missing Value Summary"):
        missing = get_missing_summary(df)
        if missing.empty:
            st.write("No missing values detected.")
        else:
            st.dataframe(missing, use_container_width=True)

    with st.expander("Data Preview (first 100 rows)"):
        st.dataframe(df.head(100), use_container_width=True)
