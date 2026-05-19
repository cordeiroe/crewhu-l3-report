import pandas as pd
import plotly.express as px
import streamlit as st
from metrics.bugfix import extract_area


def render_quarter_tab(quarter_data: list):
    if not quarter_data:
        st.info("No quarter data available.")
        return

    df = pd.DataFrame(quarter_data).rename(columns={"opened": "Opened", "closed": "Closed"})
    current_quarter = df["Quarter"].iloc[-1]

    subtab1, subtab2, subtab3 = st.tabs(["Overview", "By Area", "Backlog Trend"])

    with subtab1:
        _render_overview(df, current_quarter)

    with subtab2:
        _render_by_area(quarter_data, current_quarter)

    with subtab3:
        _render_backlog_trend(df, current_quarter)


def _render_overview(df: pd.DataFrame, current_quarter: str):
    fig = px.bar(
        df, x="Quarter", y=["Opened", "Closed"],
        text_auto=True, barmode="group",
        color_discrete_map={"Opened": "#F7724F", "Closed": "#4F8EF7"},
    )
    last_idx = len(df) - 1
    fig.add_annotation(
        x=last_idx, y=1, yref="paper",
        text="In progress",
        showarrow=False,
        font=dict(color="rgba(255,220,50,0.8)", size=11),
        yanchor="bottom",
    )
    fig.update_layout(
        xaxis_title="", yaxis_title="Tickets", legend_title="",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    summary = df.copy()
    summary["Opened Δ"] = summary["Opened"].diff().fillna(0).astype(int).map(lambda v: f"{v:+d}" if v != 0 else "—")
    summary["Closed Δ"] = summary["Closed"].diff().fillna(0).astype(int).map(lambda v: f"{v:+d}" if v != 0 else "—")
    summary["Close Rate"] = summary.apply(
        lambda r: round(r["Closed"] / r["Opened"] * 100, 1) if r["Opened"] > 0 else 0.0, axis=1
    )
    summary["Quarter"] = summary["Quarter"].apply(lambda q: f"{q} ⏳" if q == current_quarter else q)
    st.caption(f"⏳ {current_quarter} is still in progress — numbers will change as the quarter advances.")
    st.dataframe(
        summary[["Quarter", "Opened", "Opened Δ", "Closed", "Closed Δ", "Close Rate"]],
        width="stretch", hide_index=True,
        column_config={
            "Quarter": st.column_config.TextColumn("Quarter", help="Calendar quarter (Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec)."),
            "Opened": st.column_config.NumberColumn("Opened", help="Total BUGFIX tickets created during this quarter."),
            "Opened Δ": st.column_config.TextColumn("Opened Δ", help="Change vs previous quarter. Positive = more tickets opened."),
            "Closed": st.column_config.NumberColumn("Closed", help="Total BUGFIX tickets resolved during this quarter."),
            "Closed Δ": st.column_config.TextColumn("Closed Δ", help="Change vs previous quarter. Positive = more tickets resolved."),
            "Close Rate": st.column_config.NumberColumn("Close Rate", help="Closed ÷ Opened × 100. Above 100% means backlog shrank.", format="%.1f%%"),
        },
    )


def _render_by_area(quarter_data: list, current_quarter: str):
    rows = []
    for q in quarter_data:
        for ticket in q.get("tickets", []):
            rows.append({"Quarter": q["Quarter"], "Area": extract_area(ticket["Summary"])})

    if not rows:
        st.info("No ticket detail available.")
        return

    TOP_N = 8
    df = pd.DataFrame(rows)
    totals = df.groupby("Area").size()
    top_areas = totals.nlargest(TOP_N).index.tolist()
    df = df[df["Area"].isin(top_areas)]

    pivot = (
        df.groupby(["Area", "Quarter"])
        .size()
        .unstack(fill_value=0)
    )
    quarter_order = [q["Quarter"] for q in quarter_data]
    pivot = pivot.reindex(columns=[c for c in quarter_order if c in pivot.columns], fill_value=0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]

    fig = px.imshow(
        pivot,
        labels=dict(x="Quarter", y="Area", color="Tickets"),
        color_continuous_scale="Blues",
        text_auto=True,
        aspect="auto",
    )
    fig.update_layout(
        xaxis_title="", yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Tickets"),
        xaxis=dict(side="top"),
    )
    fig.update_traces(textfont=dict(size=12))
    st.plotly_chart(fig, use_container_width=True)
    other_count = len(totals) - TOP_N
    other_note = f" {other_count} less frequent area{'s' if other_count > 1 else ''} not shown." if other_count > 0 else ""
    st.caption(
        f"Top {TOP_N} areas by total closed tickets across all quarters. "
        f"Darker = more tickets.{other_note} ⏳ {current_quarter} is still in progress."
    )


def _render_backlog_trend(df: pd.DataFrame, current_quarter: str):
    trend = df.copy()
    trend["Net"] = trend["Opened"] - trend["Closed"]
    trend["Cumulative"] = trend["Net"].cumsum()

    fig = px.bar(
        trend, x="Quarter", y="Net",
        text_auto=True,
        color="Net",
        color_continuous_scale=["#4F8EF7", "#aaaaaa", "#F7724F"],
        color_continuous_midpoint=0,
    )
    fig.add_scatter(
        x=trend["Quarter"], y=trend["Cumulative"],
        mode="lines+markers", name="Cumulative",
        line=dict(color="rgba(255,220,50,0.8)", width=2),
        marker=dict(size=7),
    )
    fig.update_layout(
        xaxis_title="", yaxis_title="Tickets", legend_title="",
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Bars = net tickets per quarter (Opened − Closed). "
        "Red = backlog grew, blue = backlog shrank. "
        "Yellow line = cumulative backlog change since Q1 2025. "
        f"⏳ {current_quarter} is still in progress."
    )
