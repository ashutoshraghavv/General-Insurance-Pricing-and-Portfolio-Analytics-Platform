import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.analytics.portfolio import segment_profitability


def loss_ratio_chart(df: pd.DataFrame, segment_col: str) -> go.Figure:
    seg = segment_profitability(df, segment_col)

    fig = px.bar(
        seg,
        x=segment_col,
        y="LossRatio",
        text="LossRatio",
        color="LossRatio",
        color_continuous_scale="RdYlGn_r",
        title=f"Loss Ratio by {segment_col}",
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )

    fig.update_layout(
        height=420,
        template="plotly_white",
        coloraxis_showscale=False,
    )

    return fig


def premium_claims_chart(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.groupby(
            pd.to_datetime(df["PolicyStartDate"]).dt.to_period("M")
        )
        .agg(
            Premium=("Premium", "sum"),
            Claims=("ClaimAmount", "sum"),
        )
        .reset_index()
    )

    monthly["Month"] = monthly["PolicyStartDate"].astype(str)

    fig = px.line(
        monthly,
        x="Month",
        y=["Premium", "Claims"],
        markers=True,
        title="Premium vs Claims Trend",
    )

    fig.update_layout(
        height=420,
        template="plotly_white",
    )

    return fig