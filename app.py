from datetime import date
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from components.auth import check_auth
from components.chart import render_chart
from components.tables import render_ticket_table
from components.quarter_tab import render_quarter_tab
from services.jira import fetch_bugs, fetch_open_bugs, fetch_bugs_opened, fetch_quarter_stats
from metrics.bugfix import (
    avg_resolution_days, oldest_open_ticket, delivery_rate,
    filter_by_created, build_history,
)
from utils.date import get_week_range, format_period, calc_change, get_quarter_ranges


def main():
    check_auth()
    st.set_page_config(page_title="L3 Bugfix Report", page_icon="🐛", layout="wide")
    st.title("🐛 L3 Bugfix Delivery Report")
    st.caption(f"Generated on {date.today().strftime('%B %d, %Y')} · Project: PD · Crewhu")
    st.divider()

    last_start, last_end = get_week_range(offset_weeks=1)
    prev_start, prev_end = get_week_range(offset_weeks=2)

    with st.sidebar:
        st.header("Filters")
        exclude_tickets = st.checkbox("Exclude tickets?", value=False)
        if exclude_tickets:
            min_created = st.date_input(
                "Created before",
                value=date(2025, 1, 1),
                help="Excludes tickets created before this date from metrics and tables.",
            )
            apply_filter_to_tables = st.checkbox(
                "Also apply to ticket tables",
                value=False,
                help="When checked, the ticket lists below also exclude the filtered tickets.",
            )
        else:
            min_created = None
            apply_filter_to_tables = False
        st.divider()
        annotation_week = st.selectbox(
            "Mark a week as Backlog Cleanup",
            options=["(none)"] + [format_period(*get_week_range(w)) for w in range(6, 0, -1)],
            help="Adds a visual marker on the chart to flag a cleanup week as atypical.",
        )

    with st.spinner("Fetching data from Jira..."):
        last_bugs_raw = fetch_bugs(last_start, last_end)
        open_bugs_raw = fetch_open_bugs()
        last_opened = fetch_bugs_opened(last_start, last_end)
        prev_opened = fetch_bugs_opened(prev_start, prev_end)
        history = build_history(fetch_bugs, fetch_bugs_opened, format_period)
        quarter_ranges = get_quarter_ranges(n=6)
        quarter_data = [
            {"Quarter": q["label"], **fetch_quarter_stats(q["start"], q["end"])}
            for q in quarter_ranges
        ]

    last_bugs = filter_by_created(last_bugs_raw, min_created)
    open_bugs = filter_by_created(open_bugs_raw, min_created)
    last_bugs_table = last_bugs if apply_filter_to_tables else last_bugs_raw
    open_bugs_table = open_bugs if apply_filter_to_tables else open_bugs_raw

    last_total = len(last_bugs)
    open_total = len(open_bugs)
    net_growth = last_opened - last_total
    opened_change, opened_change_pct = calc_change(last_opened, prev_opened)
    avg_days = avg_resolution_days(last_bugs)
    oldest_key, oldest_date = oldest_open_ticket(open_bugs)
    rate = delivery_rate(last_total, open_total)

    if min_created and exclude_tickets:
        excluded = len(last_bugs_raw) - last_total
        if excluded > 0:
            st.info(f"**{excluded} ticket(s) excluded** from metrics — created before {min_created.strftime('%B %d, %Y')} (backlog cleanup filter active).")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Last Week Delivered", last_total,
        help=f"BUGFIX tickets with status Done or Released during {format_period(last_start, last_end)}.",
    )
    col2.metric(
        "Tickets Opened Last Week", last_opened,
        delta=f"{opened_change:+d} ({opened_change_pct:+.1f}%)",
        help=f"BUGFIX tickets created during {format_period(last_start, last_end)}. Delta compares to the week before.",
    )
    col3.metric(
        "Net Growth Last Week", net_growth,
        delta_color="inverse",
        help="Tickets opened minus tickets delivered last week. Negative means the backlog shrank; positive means it grew.",
    )
    col4.metric(
        "Open Tickets Today", open_total,
        help=f"All BUGFIX tickets not yet Done or Released as of {date.today().strftime('%B %d, %Y')}.",
    )

    col5, col6, col7, _ = st.columns(4)
    col5.metric(
        "Avg. Resolution Time", f"{avg_days}d",
        help=f"Average number of days between ticket creation and resolution for bugs delivered last week ({format_period(last_start, last_end)}).",
    )
    col6.metric(
        "Oldest Open Ticket", oldest_date,
        help=f"Creation date of the oldest open BUGFIX ticket still in the backlog ({oldest_key}). Indicates how long the most stalled issue has been waiting.",
    )
    col7.metric(
        "Delivery Rate", f"{rate}%",
        help=f"Percentage of known BUGFIX tickets (delivered last week + currently open) that have been resolved. Formula: {last_total} delivered ÷ ({last_total} + {open_total} open).",
    )

    st.divider()
    st.subheader("📊 Opened vs Delivered — Last 6 Weeks")
    render_chart(history, annotation_week if annotation_week != "(none)" else None)

    st.divider()
    tab1, tab2, tab3 = st.tabs([
        f"Last Week — {format_period(last_start, last_end)} ({last_total} tickets)",
        f"Open Today ({open_total} tickets)",
        "Quarter Analysis",
    ])
    with tab1:
        render_ticket_table(last_bugs_table)
    with tab2:
        render_ticket_table(open_bugs_table)
    with tab3:
        render_quarter_tab(quarter_data)


if __name__ == "__main__":
    main()
