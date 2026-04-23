"""
Call the HCDE 530 reviews API, parse JSON, and save at least 50 reviews to a CSV file.

API docs: https://brockcraft.github.io/docs/hcde530_api_documentation.html
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://hcde530-week4-api.onrender.com"
REVIEWS_URL = f"{BASE_URL.rstrip('/')}/reviews"
MIN_ROWS = 50
PAGE_SIZE = 100
OUTPUT_CSV = Path(__file__).resolve().parent / "reviews_export.csv"

EXPECTED_FIELDS = [
    "id",
    "app",
    "category",
    "rating",
    "review",
    "date",
    "helpful_votes",
    "verified_purchase",
]


def fetch_page(offset: int, limit: int) -> dict:
    """GET one page of reviews; return parsed JSON as a dict."""
    query = urllib.parse.urlencode({"offset": offset, "limit": limit})
    url = f"{REVIEWS_URL}?{query}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    records: list[dict] = []
    offset = 0

    while len(records) < MIN_ROWS:
        payload = fetch_page(offset=offset, limit=PAGE_SIZE)
        reviews = payload.get("reviews")
        if not isinstance(reviews, list):
            raise ValueError("JSON did not contain a list at key 'reviews'.")

        for item in reviews:
            if not isinstance(item, dict):
                continue
            missing = [k for k in EXPECTED_FIELDS if k not in item]
            if missing:
                raise KeyError(f"Review missing columns {missing}: {item!r}")
            records.append({k: item[k] for k in EXPECTED_FIELDS})

        returned = int(payload.get("returned", 0))
        total = int(payload.get("total", 0))
        offset += returned
        if returned == 0 or offset >= total:
            break

    if len(records) < MIN_ROWS:
        raise RuntimeError(
            f"Need at least {MIN_ROWS} records but only collected {len(records)}."
        )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        print("Request failed:", exc, file=sys.stderr)
        if "CERTIFICATE_VERIFY_FAILED" in str(exc):
            print(
                "SSL hint: try `/usr/bin/python3` or run macOS "
                "'Install Certificates.command' for your Python.",
                file=sys.stderr,
            )
        sys.exit(1)
