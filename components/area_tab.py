import pandas as pd
import plotly.express as px
import streamlit as st
from metrics.bugfix import extract_area


def render_area_tab(last_bugs: list, period_label: str):
    if not last_bugs:
        st.info("No tickets found for this period.")
        return

    df = pd.DataFrame(last_bugs)
    df["Area"] = df["Summary"].map(extract_area)

    counts = (
        df.groupby("Area", as_index=False)
        .size()
        .rename(columns={"size": "Tickets"})
        .sort_values("Tickets", ascending=False)
    )
    counts["% of Total"] = (counts["Tickets"] / counts["Tickets"].sum() * 100).round(1)

    st.subheader(f"🗂️ Tickets Delivered by Area — {period_label}")

    fig = px.bar(
        counts, x="Area", y="Tickets",
        text_auto=True,
        color="Tickets",
        color_continuous_scale=["#4F8EF7", "#1a5cba"],
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Tickets",
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        counts,
        width="stretch",
        hide_index=True,
        column_config={
            "Area": st.column_config.TextColumn("Area"),
            "Tickets": st.column_config.NumberColumn(
                "Tickets",
                help="Number of BUGFIX tickets delivered in this area last week.",
            ),
            "% of Total": st.column_config.NumberColumn(
                "% of Total",
                help="Share of total tickets delivered last week.",
                format="%.1f%%",
            ),
        },
    )
