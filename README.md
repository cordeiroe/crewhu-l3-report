# L3 Bugfix Delivery Dashboard

Weekly bugfix delivery dashboard for L3 support teams, built with Streamlit and integrated with Jira Cloud.

## Features

- **Weekly metrics** — tickets delivered, opened, net growth, open backlog, avg. resolution time, oldest open ticket, and delivery rate
- **6-week trend chart** — opened vs delivered, with optional backlog cleanup annotation
- **Quarter analysis** — historical view across the last 6 quarters with close rate metric
- **Priority sorting** — ticket tables sorted by priority (Highest → Lowest) with clickable Jira links
- **Magic link auth** — token-based access control via URL parameter
- **Sidebar filters** — exclude tickets by creation date, mark cleanup weeks on the chart

## Project Structure

```
├── app.py                  # Entry point and page layout
├── services/
│   └── jira.py             # Jira Cloud API integration
├── metrics/
│   └── bugfix.py           # Business logic and calculations
├── utils/
│   └── date.py             # Date helpers
├── components/
│   ├── auth.py             # Magic link authentication
│   ├── chart.py            # Weekly trend chart
│   ├── tables.py           # Ticket tables
│   └── quarter_tab.py      # Quarter analysis tab
└── requirements.txt
```

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `JIRA_EMAIL` | Your Atlassian account email |
| `JIRA_TOKEN` | Atlassian API token ([generate here](https://id.atlassian.com/manage-profile/security/api-tokens)) |
| `JIRA_BASE_URL` | Your Jira domain (e.g. `https://your-domain.atlassian.net`) |
| `JIRA_PROJECT` | Jira project key (e.g. `PD`) |
| `JIRA_REPORTERS` | Comma-separated list of Jira account IDs to filter by |
| `ACCESS_TOKEN` | Secret token for magic link auth (generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`) |

### 3. Run locally

```bash
streamlit run app.py
```

App runs at `http://localhost:8501`. Append `?token=YOUR_ACCESS_TOKEN` to authenticate.

## Deployment (Streamlit Cloud)

1. Push the repo to GitHub
2. Connect to [Streamlit Cloud](https://share.streamlit.io)
3. Set all environment variables listed above under **Settings → Secrets**
4. Deploy from the `main` branch — `app.py` as the entry point

Share the deployed URL with your team appending `?token=YOUR_ACCESS_TOKEN`.

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production — triggers automatic deploy on Streamlit Cloud |
| `development` | Active development — merge to `main` to publish |
