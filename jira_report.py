import os
import csv
import requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = "https://crewhu.atlassian.net"
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

REPORTERS = [
    "712020:c978dd1c-67e1-4cf4-a368-d66a5af76e2a",
    "712020:ab468b83-7ee8-44aa-b900-5fb391157dce",
    "712020:9e4c4067-5570-43a3-889f-c2c7af02b9f4",
    "712020:3aebe44d-98f7-476b-ba3f-b10e8f361f70",
]


def get_week_range(offset_weeks=0):
    today = date.today()
    monday = today - timedelta(days=today.weekday()) - timedelta(weeks=offset_weeks)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def fetch_bugs(start: date, end: date) -> list:
    reporters = ", ".join(REPORTERS)
    jql = (
        f'project = "PD" AND type = BUGFIX AND statusCategory = Done '
        f'AND reporter IN ({reporters}) '
        f'AND resolutiondate >= "{start.strftime("%Y-%m-%d")}" '
        f'AND resolutiondate <= "{end.strftime("%Y-%m-%d")}" '
        f'ORDER BY resolutiondate ASC'
    )
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    issues = []
    next_page_token = None
    try:
        while True:
            payload = {"jql": jql, "maxResults": 100, "fields": ["summary", "status", "resolutiondate"]}
            if next_page_token:
                payload["nextPageToken"] = next_page_token
            response = requests.post(url, json=payload, auth=(JIRA_EMAIL, JIRA_TOKEN), timeout=15)
            response.raise_for_status()
            data = response.json()
            for issue in data.get("issues", []):
                f = issue["fields"]
                issues.append({
                    "key": issue["key"],
                    "summary": f["summary"],
                    "status": f["status"]["name"],
                    "resolved": f["resolutiondate"][:10] if f.get("resolutiondate") else "",
                })
            if data.get("isLast", True):
                break
            next_page_token = data.get("nextPageToken")
        return issues
    except requests.exceptions.Timeout:
        print(f"ERROR: Jira API timed out after 15s for period {start} → {end}")
        raise SystemExit(1)
    except requests.exceptions.HTTPError:
        print(f"ERROR: Jira API returned {response.status_code} — check your token and project key")
        print(f"Detail: {response.text}")
        raise SystemExit(1)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not reach crewhu.atlassian.net — check your internet connection")
        raise SystemExit(1)


def format_period(start: date, end: date) -> str:
    return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"


def main():
    current_start, current_end = get_week_range(offset_weeks=1)
    previous_start, previous_end = get_week_range(offset_weeks=2)

    print(f"Fetching last week: {format_period(current_start, current_end)}")
    current_bugs = fetch_bugs(current_start, current_end)

    print(f"Fetching week before last: {format_period(previous_start, previous_end)}")
    previous_bugs = fetch_bugs(previous_start, previous_end)

    current_total = len(current_bugs)
    previous_total = len(previous_bugs)
    change = current_total - previous_total
    change_pct = round((change / previous_total) * 100, 1) if previous_total > 0 else 0.0
    trend = "▲" if change > 0 else ("▼" if change < 0 else "—")

    rows = []

    # Summary section
    rows.append(["=== WEEKLY BUGFIX DELIVERY REPORT ===", ""])
    rows.append(["Report Date", date.today().strftime("%Y-%m-%d")])
    rows.append([])
    rows.append(["=== SUMMARY ===", ""])
    rows.append(["Metric", "Value"])
    rows.append(["Last Week", format_period(current_start, current_end)])
    rows.append(["Week Before Last", format_period(previous_start, previous_end)])
    rows.append(["Bugs Delivered — Last Week", current_total])
    rows.append(["Bugs Delivered — Week Before Last", previous_total])
    rows.append(["Change (#)", f"{trend} {abs(change)}"])
    rows.append(["Change (%)", f"{trend} {abs(change_pct)}%"])
    rows.append([])

    # Last week tickets
    rows.append([f"=== TICKETS DELIVERED — LAST WEEK ({format_period(current_start, current_end)}) ===", "", "", ""])
    rows.append(["Key", "Summary", "Status", "Resolved"])
    for bug in current_bugs:
        rows.append([bug["key"], bug["summary"], bug["status"], bug["resolved"]])
    rows.append([])

    # Week before last tickets
    rows.append([f"=== TICKETS DELIVERED — WEEK BEFORE LAST ({format_period(previous_start, previous_end)}) ===", "", "", ""])
    rows.append(["Key", "Summary", "Status", "Resolved"])
    for bug in previous_bugs:
        rows.append([bug["key"], bug["summary"], bug["status"], bug["resolved"]])

    filename = f"report_{date.today().strftime('%Y-%m-%d')}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\nReport saved: {filepath}")
    print(f"  Last week       : {current_total} bugs")
    print(f"  Week before last: {previous_total} bugs")
    print(f"  Change          : {trend} {abs(change)} ({change_pct}%)")


if __name__ == "__main__":
    main()
