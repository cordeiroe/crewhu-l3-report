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

    if show_details:
        total = counts["Tickets"].sum()
        for _, row in counts.iterrows():
            area = row["Area"]
            n = int(row["Tickets"])
            pct = round(n / total * 100, 1) if total > 0 else 0.0
            area_tickets = df[df["Area"] == area].to_dict("records")
            label = f"{area} — {n} issue{'s' if n > 1 else ''} ({pct}%)"
            with st.expander(label, expanded=False):
                for t in area_tickets:
                    key = t.get("Key", "")
                    summary = t.get("Summary", "")
                    priority = t.get("Priority", "")
                    st.markdown(f"- **[{key}]({t.get('Link', '#')})** `{priority}` — {summary}")
    else:
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
