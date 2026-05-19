import pandas as pd
import streamlit as st
from metrics.bugfix import extract_area

_PRIORITY_ORDER = {"Highest": 0, "High": 1, "Medium": 2, "Low": 3, "Lowest": 4}


def render_ticket_table(bugs: list):
    if not bugs:
        st.info("No tickets found for this period.")
        return

    df = pd.DataFrame(bugs)
    df["_priority_sort"] = df["Priority"].map(lambda p: _PRIORITY_ORDER.get(p, 99))
    df = df.sort_values("_priority_sort").drop(columns=["_priority_sort"])

    df["Key"] = df["Link"]
    df["Area"] = df["Summary"].map(extract_area)
    columns = [c for c in ["Key", "Priority", "Area", "Summary", "Status", "Resolved", "Created"] if c in df.columns]
    df = df[columns]

    column_config = {
        "Key": st.column_config.LinkColumn(
            "Key",
            help="Jira ticket identifier. Click to open in Jira.",
            display_text=r"https://crewhu\.atlassian\.net/browse/(PD-\d+)",
        ),
        "Priority": st.column_config.TextColumn(
            "Priority",
            help="Ticket priority as defined in Jira: Highest → High → Medium → Low → Lowest.",
        ),
        "Area": st.column_config.TextColumn(
            "Area",
            help="Product area extracted from the ticket title prefix (e.g. [TRENDS], [HUB], [CREWHU]). Shows — when no prefix is present.",
        ),
        "Summary": st.column_config.TextColumn(
            "Summary",
            help="Ticket title.",
        ),
        "Status": st.column_config.TextColumn(
            "Status",
            help="Current status of the ticket in Jira.",
        ),
        "Resolved": st.column_config.TextColumn(
            "Resolved",
            help="Date the ticket was marked as Done or Released.",
        ),
        "Created": st.column_config.TextColumn(
            "Created",
            help="Date the ticket was originally created.",
        ),
    }

    st.dataframe(df, width="stretch", hide_index=True, column_config=column_config)
