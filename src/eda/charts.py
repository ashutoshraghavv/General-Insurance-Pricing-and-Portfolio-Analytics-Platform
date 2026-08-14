"""Interactive Plotly charts for exploratory analytics."""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


CHART_THEME = {
    "template": "plotly_white",
    "color_discrete_sequence": px.colors.qualitative.Safe,
}


def distribution_chart(
    df: pd.DataFrame, column: str, title: str, nbins: int = 40
) -> go.Figure:
    """Histogram for a numeric column."""
    fig = px.histogram(
        df,
        x=column,
        nbins=nbins,
        title=title,
        labels={column: column},
        **CHART_THEME,
    )
    fig.update_layout(bargap=0.05, height=380)
    return fig


def claim_frequency_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of claim count frequency."""
    counts = df["ClaimCount"].value_counts().sort_index().reset_index()
    counts.columns = ["ClaimCount", "Policies"]
    fig = px.bar(
        counts,
        x="ClaimCount",
        y="Policies",
        title="Claim Frequency Distribution",
        **CHART_THEME,
    )
    fig.update_layout(height=380)
    return fig


def claim_severity_chart(df: pd.DataFrame) -> go.Figure:
    """Histogram of average severity for policies with claims."""
    claims = df[df["ClaimCount"] > 0].copy()
    claims["Severity"] = claims["ClaimAmount"] / claims["ClaimCount"]
    fig = px.histogram(
        claims,
        x="Severity",
        nbins=40,
        title="Claim Severity Distribution (Policies with Claims)",
        labels={"Severity": "Average Claim Severity"},
        **CHART_THEME,
    )
    fig.update_layout(height=380)
    return fig


def monthly_trends_chart(df: pd.DataFrame) -> go.Figure:
    """Monthly premium, claims, and loss ratio trends."""
    data = df.copy()
    data["Month"] = pd.to_datetime(data["PolicyStartDate"]).dt.to_period("M").astype(str)
    monthly = (
        data.groupby("Month")
        .agg(
            WrittenPremium=("Premium", "sum"),
            TotalClaims=("ClaimAmount", "sum"),
            Exposure=("Exposure", "sum"),
        )
        .reset_index()
    )
    monthly["LossRatio"] = (monthly["TotalClaims"] / monthly["WrittenPremium"] * 100).round(
        2
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=monthly["Month"], y=monthly["WrittenPremium"], name="Written Premium"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["TotalClaims"],
            name="Total Claims",
            mode="lines+markers",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["LossRatio"],
            name="Loss Ratio %",
            mode="lines+markers",
            line=dict(dash="dot"),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Monthly Premium, Claims & Loss Ratio Trends",
        template="plotly_white",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_yaxes(title_text="Amount", secondary_y=False)
    fig.update_yaxes(title_text="Loss Ratio %", secondary_y=True)
    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Correlation heatmap for numeric columns."""
    numeric_cols = ["Exposure", "Premium", "ClaimCount", "ClaimAmount", "Age", "VehicleAge"]
    available = [c for c in numeric_cols if c in df.columns]
    corr = df[available].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        title="Correlation Heatmap",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1, 
    )
    fig.update_layout(height=420)
    return fig


def segment_analysis_chart(
    df: pd.DataFrame, segment_col: str, metric: str = "LossRatio"
) -> go.Figure:
    """Segment-level bar chart for a chosen metric."""

    grouped = (
        df.groupby(segment_col)
        .agg(
            WrittenPremium=("Premium", "sum"),
            TotalClaims=("ClaimAmount", "sum"),
            TotalClaimCount=("ClaimCount", "sum"),
            Exposure=("Exposure", "sum"),
            PolicyCount=("PolicyID", "count"),
        )
        .reset_index()
    )

    grouped["LossRatio"] = (
        grouped["TotalClaims"] / grouped["WrittenPremium"] * 100
    ).round(2)

    grouped["ClaimFrequency"] = (
        grouped["TotalClaimCount"] / grouped["Exposure"]
    ).round(4)

    severity_df = (
        df[df["ClaimCount"] > 0]
        .groupby(segment_col)
        .agg(
            TotalClaimAmount=("ClaimAmount", "sum"),
            TotalClaimCount=("ClaimCount", "sum"),
        )
    )

    severity_df["AvgSeverity"] = (
        severity_df["TotalClaimAmount"]
        / severity_df["TotalClaimCount"]
    )

    grouped["AvgSeverity"] = (
        grouped[segment_col]
        .map(severity_df["AvgSeverity"])
        .fillna(0)
        .round(2)
    )

    y_col = metric if metric in grouped.columns else "LossRatio"

    fig = px.bar(
        grouped,
        x=segment_col,
        y=y_col,
        title=f"{metric} by {segment_col}",
        text=y_col,
        **CHART_THEME,
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
    )

    fig.update_layout(
        height=380,
        xaxis_title=segment_col,
        yaxis_title=y_col,
    )

    return fig