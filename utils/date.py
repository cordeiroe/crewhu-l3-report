from datetime import date, timedelta


def get_week_range(offset_weeks=0):
    today = date.today()
    monday = today - timedelta(days=today.weekday()) - timedelta(weeks=offset_weeks)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def format_period(start: date, end: date) -> str:
    return f"{start.strftime('%b %d')} – {end.strftime('%b %d, %Y')}"


def calc_change(current: int, previous: int) -> tuple:
    change = current - previous
    pct = round((change / previous) * 100, 1) if previous > 0 else 0.0
    return change, pct


def get_quarter_ranges(n: int = 6):
    today = date.today()
    current_quarter = (today.month - 1) // 3
    current_year = today.year

    quarters = []
    q = current_quarter
    y = current_year

    for _ in range(n):
        q_start_month = q * 3 + 1
        q_end_month = q_start_month + 2
        q_start = date(y, q_start_month, 1)
        if q_end_month == 12:
            q_end = date(y, 12, 31)
        else:
            q_end = date(y, q_end_month + 1, 1) - timedelta(days=1)

        quarters.append({
            "label": f"Q{q + 1} {y}",
            "start": q_start,
            "end": min(q_end, today),
        })

        q -= 1
        if q < 0:
            q = 3
            y -= 1

    return list(reversed(quarters))
