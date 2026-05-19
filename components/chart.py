from typing import Optional
import plotly.express as px
import streamlit as st


def render_chart(history: list, annotation_week: Optional[str]):
    import pandas as pd
    df = pd.DataFrame(history)
    fig = px.bar(
        df, x="Week", y=["Bugs Delivered", "Bugs Opened"],
        text_auto=True, barmode="group",
        color_discrete_map={"Bugs Delivered": "#4F8EF7", "Bugs Opened": "#F7724F"},
    )
    if annotation_week and annotation_week in df["Week"].values:
        idx = df["Week"].tolist().index(annotation_week)
        fig.add_vline(
            x=idx,
            line_dash="dash",
            line_color="rgba(255,220,50,0.6)",
            annotation_text="Backlog Cleanup",
            annotation_position="top",
            annotation_font_color="rgba(255,220,50,0.9)",
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
