import os
import requests
import streamlit as st
from datetime import date
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("JIRA_BASE_URL")
PROJECT = os.getenv("JIRA_PROJECT")
AUTH = (os.getenv("JIRA_EMAIL"), os.getenv("JIRA_TOKEN"))
REPORTERS = [r.strip() for r in os.getenv("JIRA_REPORTERS", "").split(",") if r.strip()]

_SEARCH_URL = f"{BASE_URL}/rest/api/3/search/jql"
_REPORTERS_JQL = ", ".join(REPORTERS)



def _paginate(jql: str, fields: list[str]) -> list[dict]:
    issues, next_page_token = [], None
    while True:
        payload = {"jql": jql, "maxResults": 100, "fields": fields}
        if next_page_token:
            payload["nextPageToken"] = next_page_token
        try:
            r = requests.post(_SEARCH_URL, json=payload, auth=AUTH, timeout=15)
            r.raise_for_status()
        except requests.exceptions.Timeout:
            st.error("Jira API timed out. Please try again.")
            return []
        except requests.exceptions.HTTPError:
            st.error(f"Jira API error {r.status_code}. Check your credentials.")
            return []
        except requests.exceptions.ConnectionError:
            st.error(f"Could not reach {BASE_URL}. Check your connection.")
            return []
        data = r.json()
        issues.extend(data.get("issues", []))
        if data.get("isLast", True):
            break
        next_page_token = data.get("nextPageToken")
    return issues


@st.cache_data(ttl=3600)
def fetch_bugs(start: date, end: date) -> list[dict]:
    jql = (
        f'project = "{PROJECT}" AND type = BUGFIX AND statusCategory = Done '
        f'AND reporter IN ({_REPORTERS_JQL}) '
        f'AND resolutiondate >= "{start}" AND resolutiondate <= "{end}" '
        f'ORDER BY resolutiondate ASC'
    )
    result = []
    for issue in _paginate(jql, ["summary", "status", "resolutiondate", "created", "priority"]):
        f = issue["fields"]
        status = f["status"]["name"]
        result.append({
            "Key": issue["key"],
            "Link": f"{BASE_URL}/browse/{issue['key']}",
            "Priority": f["priority"]["name"] if f.get("priority") else "Medium",
            "Summary": f["summary"],
            "Status": "Done" if status == "Concluído" else status,
            "Resolved": f["resolutiondate"][:10] if f.get("resolutiondate") else "",
            "Created": f["created"][:10] if f.get("created") else "",
        })
    return result


@st.cache_data(ttl=3600)
def fetch_open_bugs() -> list[dict]:
    jql = (
        f'project = "{PROJECT}" AND type = BUGFIX AND statusCategory != Done '
        f'AND reporter IN ({_REPORTERS_JQL}) '
        f'ORDER BY created ASC'
    )
    result = []
    for issue in _paginate(jql, ["summary", "status", "created", "priority"]):
        f = issue["fields"]
        result.append({
            "Key": issue["key"],
            "Link": f"{BASE_URL}/browse/{issue['key']}",
            "Priority": f["priority"]["name"] if f.get("priority") else "Medium",
            "Summary": f["summary"],
            "Status": f["status"]["name"],
            "Created": f["created"][:10] if f.get("created") else "",
        })
    return result


@st.cache_data(ttl=3600)
def fetch_bugs_opened(start: date, end: date) -> int:
    jql = (
        f'project = "{PROJECT}" AND type = BUGFIX '
        f'AND reporter IN ({_REPORTERS_JQL}) '
        f'AND created >= "{start}" AND created <= "{end}"'
    )
    return len(_paginate(jql, ["id"]))


@st.cache_data(ttl=3600)
def fetch_bugs_opened_detail(start: date, end: date) -> list[dict]:
    jql = (
        f'project = "{PROJECT}" AND type = BUGFIX '
        f'AND reporter IN ({_REPORTERS_JQL}) '
        f'AND created >= "{start}" AND created <= "{end}"'
    )
    result = []
    for issue in _paginate(jql, ["summary", "priority", "created"]):
        f = issue["fields"]
        result.append({
            "Key": issue["key"],
            "Link": f"{BASE_URL}/browse/{issue['key']}",
            "Summary": f["summary"],
            "Priority": f["priority"]["name"] if f.get("priority") else "Medium",
            "Created": f["created"][:10] if f.get("created") else "",
        })
    return result


@st.cache_data(ttl=3600)
def fetch_quarter_stats(start: date, end: date) -> dict:
    opened = len(_paginate(
        f'project = "{PROJECT}" AND type = BUGFIX AND reporter IN ({_REPORTERS_JQL}) '
        f'AND created >= "{start}" AND created <= "{end}"',
        ["id"],
    ))
    closed = len(_paginate(
        f'project = "{PROJECT}" AND type = BUGFIX AND statusCategory = Done '
        f'AND reporter IN ({_REPORTERS_JQL}) '
        f'AND resolutiondate >= "{start}" AND resolutiondate <= "{end}"',
        ["id"],
    ))
    return {"opened": opened, "closed": closed}
