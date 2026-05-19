# L3 Bugfix Report — Streamlit Dashboard

Internal weekly bugfix delivery dashboard for Crewhu's L3 team leadership.

## Project Structure

```
L3Reports/
├── app.py                  # UI layout and Streamlit orchestration
├── services/
│   ├── __init__.py
│   └── jira.py             # Jira Cloud API integration
├── metrics/
│   ├── __init__.py
│   └── bugfix.py           # Business logic calculations
├── utils/
│   ├── __init__.py
│   └── date.py             # Date helpers and week/quarter ranges
├── components/
│   ├── __init__.py
│   ├── auth.py             # Magic link authentication
│   ├── chart.py            # Opened vs Delivered bar chart
│   ├── tables.py           # Ticket tables with priority sort + LinkColumn
│   └── quarter_tab.py      # Quarter Analysis tab (chart + summary table)
├── .env                    # Credentials (never commit)
├── .env.example            # Credential template
├── requirements.txt        # Python dependencies
└── CLAUDE.md               # This file
```

## Running Locally

```bash
streamlit run app.py
```

App runs at `http://localhost:8501`. Leave `ACCESS_TOKEN` empty or absent in `.env` to skip magic link locally.

Hot-reload is automatic for `.py` changes. Only restart if `.env` changes.

## Environment Variables

All sensitive config lives in `.env` (local) or Streamlit Cloud Secrets (production). The required variables and their expected format are defined in `.env.example`.

Generate the Jira API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Deploy

- **Repo:** `github.com/cordeiroe/jira-delivery-dashboard` (public, personal account)
- **Branch strategy:** `development` → daily work → PR to `main` → auto-deploy on Streamlit Cloud
- **Secrets on Streamlit Cloud:** same 6 variables listed above — configure in Settings → Secrets

### ⚠️ Pre-deploy checklist

Before any merge to `main` or deploy, confirm with a screenshot that all 6 secrets are set in Streamlit Cloud (Settings → Secrets). No visual confirmation = no deploy authorized.

### Troubleshooting: stale deploy

If Streamlit Cloud is running old code (e.g., `ImportError` from old import paths), the root cause is usually a stale git checkout — not a code error. Fix: go to the Streamlit Cloud dashboard and **Reboot** the app. This forces a fresh git pull without changing the app URL.

## Jira Configuration

- **Domain:** `crewhu.atlassian.net` (`JIRA_BASE_URL` env var)
- **Project:** `PD` (`JIRA_PROJECT` env var)
- **Issue type:** `BUGFIX`
- **Delivered status:** `statusCategory = Done` (covers `Concluído` and `Released`)
- **API endpoint:** `POST /rest/api/3/search/jql` (v2 and GET /search are deprecated — 410)
- **Reporters:** 4 account IDs in `JIRA_REPORTERS` env var
- **Week comparison:** last week (offset 1) vs week before last (offset 2)
- **Weeks are Monday–Sunday**

## Key Decisions

- `statusCategory = Done` avoids Portuguese/English encoding issues (`Concluído` vs `Done`)
- Jira search API does not return `total` — pagination via `isLast` + `nextPageToken`
- Cache TTL is 1 hour (`ttl=3600`) on all Jira fetch functions
- Python 3.9 — use `Optional[str]` from `typing`, not `str | None`
- Dates are treated as UTC literals — no timezone conversion to BRT

## Metrics

| Metric | Description |
|---|---|
| Last Week Delivered | BUGFIX tickets resolved last week |
| Tickets Opened Last Week | Created last week (with delta vs week before) |
| Net Growth Last Week | Opened minus delivered — negative = backlog shrank |
| Open Tickets Today | All open BUGFIX tickets as of today |
| Avg. Resolution Time | Average days creation → resolution (last week) |
| Oldest Open Ticket | Creation date of the oldest unresolved ticket |
| Delivery Rate | Delivered ÷ (delivered + open) × 100 |

## Sidebar Filters

- **Exclude tickets?** — exclude tickets created before a given date (backlog cleanup filter)
- **Also apply to ticket tables** — extends filter to ticket listing tabs
- **Mark a week as Backlog Cleanup** — dashed annotation on chart for selected week

## Quarter Analysis Tab

- Bar chart: Opened vs Closed per quarter (last 6 quarters)
- Current quarter marked as "In progress" on chart and with ⏳ in table
- Summary table: Opened, Closed, Close Rate (Closed ÷ Opened × 100%), Δ columns
- Close Rate = primary health metric for the quarter view

## Backlog

- **Trending de tópicos:** Coluna na tabela de tickets identificando padrões/tags (generalizado vs isolado) via labels ou components do Jira
- **`use_container_width` deprecation:** Substituir por `width='stretch'` — deadline Streamlit 2025-12-31
