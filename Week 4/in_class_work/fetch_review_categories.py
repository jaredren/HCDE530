"""
Fetch app reviews from the HCDE 530 Week 4 API, filter and summarize, then save CSV.

API: https://brockcraft.github.io/docs/hcde530_api_documentation.html
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_URL = "https://hcde530-week4-api.onrender.com"
REVIEWS_PATH = "/reviews"
PAGE_SIZE = 100
OUTPUT_CSV = Path(__file__).resolve().parent / "api_review_analysis.csv"


def fetch_page(offset: int, limit: int) -> dict:
    """Return one page of the API response as a dict."""
    params = urllib.parse.urlencode({"offset": offset, "limit": limit})
    url = f"{BASE_URL.rstrip('/')}{REVIEWS_PATH}?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_all_reviews() -> list[dict]:
    """Download every review using offset/limit pagination."""
    all_reviews: list[dict] = []
    offset = 0
    while True:
        data = fetch_page(offset=offset, limit=PAGE_SIZE)
        reviews = data.get("reviews")
        if not isinstance(reviews, list):
            raise ValueError("API response missing a list field 'reviews'.")
        required = {"category", "helpful_votes", "verified_purchase"}
        for review in reviews:
            if not isinstance(review, dict):
                continue
            if required - review.keys():
                raise KeyError(f"Review missing keys {required - review.keys()}: {review!r}")
            all_reviews.append(review)
        returned = int(data.get("returned", 0))
        total = int(data.get("total", 0))
        offset += returned
        if offset >= total or returned == 0:
            break
    return all_reviews


def main() -> None:
    reviews = fetch_all_reviews()
    print(f"Loaded {len(reviews)} reviews from the API.")

    filtered = [
        r for r in reviews if r["verified_purchase"] is True
    ]  # filter: only verified purchases

    votes_by_category: dict[str, list[int]] = defaultdict(list)
    for r in filtered:
        votes_by_category[str(r["category"])].append(int(r["helpful_votes"]))

    summary_rows: list[dict[str, object]] = []
    for category in sorted(votes_by_category):
        votes = votes_by_category[category]
        summary_rows.append(
            {
                "category": category,
                "verified_review_count": len(votes),
                "max_helpful_votes": max(votes),
                "min_helpful_votes": min(votes),
            }
        )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "category",
        "verified_review_count",
        "max_helpful_votes",
        "min_helpful_votes",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nVerified reviews after filter: {len(filtered)}")
    print("Occurrences by category (verified only):")
    for row in summary_rows:
        print(f"  {row['category']}: {row['verified_review_count']} reviews")

    if filtered:
        top = max(filtered, key=lambda r: int(r["helpful_votes"]))  # highest numeric helpful_votes
        bottom = min(filtered, key=lambda r: int(r["helpful_votes"]))
        print("\nHighest helpful_votes (among filtered):")
        print(
            f"  id={top['id']}, category={top['category']}, "
            f"helpful_votes={top['helpful_votes']}"
        )
        print("Lowest helpful_votes (among filtered):")
        print(
            f"  id={bottom['id']}, category={bottom['category']}, "
            f"helpful_votes={bottom['helpful_votes']}"
        )

    print(f"\nWrote {len(summary_rows)} summary rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as e:
        print("Network error while calling the API:", e, file=sys.stderr)
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            print(
                "Hint: On macOS with python.org Python, run the "
                "'Install Certificates.command' script in your Python folder, "
                "or use a Python install that includes up-to-date CA certificates.",
                file=sys.stderr,
            )
        sys.exit(1)
