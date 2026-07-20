"""Fetch the public GitHub contribution calendar and write data/contributions.json.

Scrapes https://github.com/users/<user>/contributions — no token required.
"""

import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Haaris-7"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

COUNT_RE = re.compile(r"^(\d+|No) contributions? on (.+)$")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tooltips = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        match = COUNT_RE.match(tip.get_text(strip=True))
        if target and match:
            tooltips[target] = 0 if match.group(1) == "No" else int(match.group(1))

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        day_date = cell.get("data-date")
        if not day_date:
            continue
        level = int(cell.get("data-level", 0))
        count = tooltips.get(cell.get("id"))
        if count is None:
            count = level
        days.append({"date": day_date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default=None)

    longest = current = 0
    streak = 0
    for d in days:
        streak = streak + 1 if d["count"] > 0 else 0
        longest = max(longest, streak)

    today = date.today()
    by_date = {d["date"]: d["count"] for d in days}
    cursor = today
    if by_date.get(cursor.isoformat(), 0) == 0:
        cursor -= timedelta(days=1)
    while by_date.get(cursor.isoformat(), 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]} if best else None,
        "longest_streak": longest,
        "current_streak": current,
        "monthly": dict(sorted(monthly.items())),
    }


def main():
    days = fetch_days()
    if not days:
        print("No contribution cells parsed — GitHub markup may have changed.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "stats": compute_stats(days),
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT} — {len(days)} days, {payload['stats']['total']} contributions")


if __name__ == "__main__":
    main()
