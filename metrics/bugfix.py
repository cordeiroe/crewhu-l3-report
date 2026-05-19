from datetime import datetime
from typing import Optional
from utils.date import get_week_range


def avg_resolution_days(bugs: list) -> float:
    days = []
    for bug in bugs:
        if bug.get("Created") and bug.get("Resolved"):
            created = datetime.strptime(bug["Created"], "%Y-%m-%d")
            resolved = datetime.strptime(bug["Resolved"], "%Y-%m-%d")
            days.append((resolved - created).days)
    return round(sum(days) / len(days), 1) if days else 0.0


def oldest_open_ticket(bugs: list) -> tuple:
    valid = [b for b in bugs if b.get("Created")]
    if not valid:
        return "—", "—"
    oldest = min(valid, key=lambda b: b["Created"])
    return oldest["Key"], oldest["Created"]


def delivery_rate(delivered: int, open_total: int) -> float:
    total = delivered + open_total
    return round((delivered / total) * 100, 1) if total > 0 else 0.0


def filter_by_created(bugs: list, min_date: Optional[object]) -> list:
    if not min_date:
        return bugs
    return [b for b in bugs if b.get("Created") and b["Created"] >= min_date.isoformat()]


def build_history(fetch_bugs_fn, fetch_bugs_opened_fn, format_period_fn) -> list:
    return [
        {
            "Week": format_period_fn(*get_week_range(w)),
            "Bugs Delivered": len(fetch_bugs_fn(*get_week_range(w))),
            "Bugs Opened": fetch_bugs_opened_fn(*get_week_range(w)),
        }
        for w in range(6, 0, -1)
    ]
