import pandas as pd
import plotly.express as px
import streamlit as st
from metrics.bugfix import extract_area


def render_area_tab(bugs: list, period_label: str, show_details: bool = False):
    if not bugs:
        st.info("No issues found for this period.")
        return

    df = pd.DataFrame(bugs)
    df["Area"] = df["Summary"].map(extract_area)

    counts = (
        df.groupby("Area", as_index=False)
        .size()
        .rename(columns={"size": "Tickets"})
        .sort_values("Tickets", ascending=False)
    )
    counts["% of Total"] = (counts["Tickets"] / counts["Tickets"].sum() * 100).round(1)

    if show_details:
        total = counts["Tickets"].sum()
        for _, row in counts.iterrows():
            area = row["Area"]
            n = int(row["Tickets"])
            pct = round(n / total * 100, 1) if total > 0 else 0.0
            area_df = df[df["Area"] == area].copy()
            area_df["Key"] = area_df["Link"]
            cols = [c for c in ["Key", "Priority", "Status", "Summary"] if c in area_df.columns]
            area_df = area_df[cols]
            label = f"{area} — {n} issue{'s' if n > 1 else ''} ({pct}%)"
            with st.expander(label, expanded=False):
                st.dataframe(
                    area_df,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Key": st.column_config.LinkColumn(
                            "Key",
                            help="Jira issue identifier. Click to open in Jira.",
                            display_text=r"https://crewhu\.atlassian\.net/browse/(PD-\d+)",
                        ),
                        "Priority": st.column_config.TextColumn("Priority"),
                        "Status": st.column_config.TextColumn(
                            "Status", help="Current status of the issue in Jira."
                        ),
                        "Summary": st.column_config.TextColumn("Summary"),
                    },
                )
    else:
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
                "Tickets": st.column_config.NumberColumn("Tickets"),
                "% of Total": st.column_config.NumberColumn(
                    "% of Total",
                    format="%.1f%%",
                ),
            },
        )
