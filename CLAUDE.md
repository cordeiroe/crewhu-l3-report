# L3 Bugfix Report — Streamlit Dashboard

Internal weekly bugfix delivery dashboard for Crewhu's L3 team leadership.

## Project Structure

```
L3Reports/
├── app.py          # UI layout and Streamlit logic
├── jira.py         # Jira Cloud API integration
├── utils.py        # Date helpers and calculations
├── jira_report.py  # Legacy CSV export script (kept for reference)
├── .env            # Credentials (never commit)
├── .env.example    # Credential template
└── CLAUDE.md       # This file
```

## Running Locally

```bash
/Users/cordeiroe/Library/Python/3.9/bin/streamlit run app.py --server.headless true --browser.gatherUsageStats false
```

App runs at `http://localhost:8501`.

## Environment Variables

```
JIRA_EMAIL=your-jira-email@crewhu.com
JIRA_TOKEN=your-atlassian-api-token
```

Generate the API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Jira Configuration

- **Domain:** `crewhu.atlassian.net`
- **Project:** `PD`
- **Issue type:** `BUGFIX`
- **Delivered status:** `statusCategory = Done` (covers `Concluído` and `Released`)
- **API endpoint:** `POST /rest/api/3/search/jql` (v2 and GET /search are deprecated — 410)
- **Reporters:** 4 account IDs hardcoded in `jira.py` under `REPORTERS`
- **Week comparison:** last week (offset 1) vs week before last (offset 2)
- **Weeks are Monday–Sunday**

## Key Decisions

- `statusCategory = Done` is used instead of status names to avoid Portuguese/English encoding issues (`Concluído` vs `Done`)
- The new Jira search API does not return `total` — pagination via `isLast` and `nextPageToken` is required
- Cache TTL is 1 hour (`ttl=3600`) on all Jira fetch functions
- Python 3.9 is in use — avoid `str | None` union syntax; use `Optional[str]` from `typing`

## Metrics

| Metric | Description |
|---|---|
| Last Week Delivered | BUGFIX tickets resolved last week |
| Tickets Opened Last Week | BUGFIX tickets created last week (delta vs week before) |
| Net Growth Last Week | Opened minus delivered — negative means backlog shrank |
| Open Tickets Today | All open BUGFIX tickets as of today |
| Avg. Resolution Time | Average days from creation to resolution (last week) |
| Oldest Open Ticket | Creation date of the oldest unresolved ticket |
| Delivery Rate | Delivered ÷ (delivered + open) × 100 |

## Sidebar Filters

- **Exclude tickets?** — when checked, enables a date picker to exclude tickets created before a given date from metrics (useful for backlog cleanup weeks)
- **Also apply to ticket tables** — extends the filter to the ticket listing tabs
- **Mark a week as Backlog Cleanup** — adds a dashed annotation line on the chart for the selected week

## Dependencies

```bash
pip3 install streamlit plotly pandas requests python-dotenv
```

## Next Steps

- Deploy to Streamlit Cloud (GitHub repo required)
- Set `JIRA_EMAIL` and `JIRA_TOKEN` as environment variables in Streamlit Cloud settings
