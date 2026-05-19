import pandas as pd
import plotly.express as px
import streamlit as st


def render_quarter_tab(quarter_data: list):
    if not quarter_data:
        st.info("No quarter data available.")
        return

    df = pd.DataFrame(quarter_data).rename(columns={"opened": "Opened", "closed": "Closed"})
    current_quarter = df["Quarter"].iloc[-1]

    st.subheader("📅 Opened vs Closed — Last 6 Quarters")
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
        xaxis_title="",
        yaxis_title="Tickets",
        legend_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Quarter Summary")
    summary = df.copy()
    summary["Opened Δ"] = summary["Opened"].diff().fillna(0).astype(int).map(lambda v: f"{v:+d}" if v != 0 else "—")
    summary["Closed Δ"] = summary["Closed"].diff().fillna(0).astype(int).map(lambda v: f"{v:+d}" if v != 0 else "—")
    summary["Close Rate"] = summary.apply(
        lambda r: round(r["Closed"] / r["Opened"] * 100, 1) if r["Opened"] > 0 else 0.0, axis=1
    )
    summary["Quarter"] = summary["Quarter"].apply(
        lambda q: f"{q} ⏳" if q == current_quarter else q
    )
    st.caption(f"⏳ {current_quarter} is still in progress — numbers will change as the quarter advances.")

    st.dataframe(
        summary[["Quarter", "Opened", "Opened Δ", "Closed", "Closed Δ", "Close Rate"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quarter": st.column_config.TextColumn(
                "Quarter",
                help="Calendar quarter (Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec).",
            ),
            "Opened": st.column_config.NumberColumn(
                "Opened",
                help="Total BUGFIX tickets created during this quarter.",
            ),
            "Opened Δ": st.column_config.TextColumn(
                "Opened Δ",
                help="Change in tickets opened compared to the previous quarter. Positive means more tickets were opened.",
            ),
            "Closed": st.column_config.NumberColumn(
                "Closed",
                help="Total BUGFIX tickets resolved (Done or Released) during this quarter.",
            ),
            "Closed Δ": st.column_config.TextColumn(
                "Closed Δ",
                help="Change in tickets closed compared to the previous quarter. Positive means more tickets were resolved.",
            ),
            "Close Rate": st.column_config.NumberColumn(
                "Close Rate",
                help="Closed ÷ Opened × 100. Above 100% means the backlog shrank (more resolved than created). Below 100% means it grew.",
                format="%.1f%%",
            ),
        },
    )
