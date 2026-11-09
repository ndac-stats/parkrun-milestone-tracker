"""Fetch public parkrun athlete histories and publish a small JSON snapshot.

Use sparingly. This workflow is scheduled weekly, not continuously.
The parkrun site has no public results API; HTML structure/access can change.
"""
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ATHLETES_FILE = ROOT / "config" / "athletes.csv"
OUTPUT_FILE = ROOT / "data" / "milestones.json"
BASE_URL = "https://www.parkrun.com.au/results/athleteresultshistory/"
HEADERS = {
    "User-Agent": "CommunityMilestoneTracker/1.0 (weekly public-results snapshot)"
}
MILESTONES = [
    10,
    25,
    50,
    100,
    150,
    200,
    250,
    300,
    350,
    400,
    450,
    500,
    1000]


def read_athletes():
    with ATHLETES_FILE.open(newline="", encoding="utf-8-sig") as f:
        return [row for row in csv.DictReader(f) if row.get("athlete_id", "").strip()]


def parse_total_runs(soup):
    # The parkrun history page has changed markup over time. First look for
    # an explicit total in headings/text, then fall back to counting result rows.
    text = soup.get_text(" ", strip=True)
    patterns = [
        r"(\d[\d,]*)\s+parkruns?\b",
        r"total\s+(?:number\s+of\s+)?runs?\s*[:\-]?\s*(\d[\d,]*)",
        r"(\d[\d,]*)\s+events?\s+completed\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))

    tables = soup.select("table#results")
    if tables:
        # Athlete history is commonly the second results table. Prefer the
        # table with the greatest number of body rows, ignoring header rows.
        row_counts = []
        for table in tables:
            rows = table.select("tbody tr")
            if not rows:
                rows = table.select("tr")
                rows = [row for row in rows if row.find("td")]
            row_counts.append(len(rows))
        if row_counts:
            return max(row_counts)
    raise ValueError("Could not determine total run count from the athlete history page")


def parse_name(soup, fallback):
    heading = soup.find("h2")
    if heading:
        name = heading.get_text(" ", strip=True)
        if name:
            return name
    title = soup.find("title")
    if title:
        name = title.get_text(" ", strip=True)
        if name:
            return name
    return fallback


def fetch_athlete(session, athlete):
    athlete_id = athlete["athlete_id"].strip()
    params = urlencode({"athleteNumber": athlete_id, "eventNumber": "0"})
    url = f"{BASE_URL}?{params}"
    response = session.get(url, headers=HEADERS, timeout=35)
    response.raise_for_status()
    if len(response.text) < 500 or "athlete" not in response.text.lower():
        raise ValueError("Response did not look like a parkrun athlete history page")
    soup = BeautifulSoup(response.text, "html.parser")
    total = parse_total_runs(soup)
    name = parse_name(soup, athlete.get("name", "").strip() or athlete_id)
    return {
        "athlete_id": athlete_id,
        "name": name,
        "total_runs": total,
        "last_run_date": None,
        "profile_url": f"https://www.parkrun.com.au/parkrunner/{athlete_id}/",
        "milestones_reached": [m for m in MILESTONES if total >= m],
    }


def main():
    athletes = read_athletes()
    if not athletes:
        raise SystemExit("No athlete IDs found in config/athletes.csv")

    session = requests.Session()
    runners, failures = [], []
    for index, athlete in enumerate(athletes):
        try:
            runners.append(fetch_athlete(session, athlete))
            print(f"Fetched {athlete['athlete_id']}: {runners[-1]['total_runs']} runs")
        except Exception as exc:
            failures.append(f"{athlete['athlete_id']}: {exc}")
            print(f"FAILED {athlete['athlete_id']}: {exc}", file=sys.stderr)
        # A deliberate pause between requests to avoid hammering the site.
        if index < len(athletes) - 1:
            time.sleep(3)

    # Do not overwrite a previously good snapshot if every request failed.
    if not runners:
        raise SystemExit("Every athlete request failed; existing data was left untouched.")

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            f"Weekly snapshot. {len(runners)} of {len(athletes)} athlete profiles updated."
            + (f" {len(failures)} profile(s) could not be refreshed." if failures else "")
        ),
        "runners": sorted(runners, key=lambda r: r["total_runs"], reverse=True),
        "failures": failures,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
