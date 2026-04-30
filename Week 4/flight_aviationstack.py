"""
Call AviationStack's flight endpoint using an access key from `.env` in this folder.

Docs: https://aviationstack.com/documentation
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Resolve paths next to this script so `.env` and the output CSV stay together for grading.
HERE = Path(__file__).resolve().parent
ENV_PATH = HERE / ".env"
OUTPUT_CSV = HERE / "aviationstack_flights_sample.csv"


def load_env_file(path: Path) -> None:
    """Read KEY=value lines into os.environ so os.environ.get can pick up secrets."""
    if not path.exists():
        raise FileNotFoundError(f"Missing {path} — create it beside this script with your AviationStack key.")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"" )
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    load_env_file(ENV_PATH)

    # AviationStack expects `access_key` in the query string; read it from the environment, never hard-code it.
    access_key = os.environ.get("AVIATIONSTACK_ACCESS_KEY") or os.environ.get("MY_API_KEY")
    if not access_key:
        print(
            "Set AVIATIONSTACK_ACCESS_KEY or MY_API_KEY in .env next to this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    # This URL hits the `/v1/flights` collection; `limit` keeps the free-tier payload small and fast.
    base_url = "https://api.aviationstack.com/v1/flights"
    params = {"access_key": access_key, "limit": 10}
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    # The API answers with JSON: metadata plus a `data` array of flight objects (each object is deeply nested).
    request = urllib.request.Request(
        full_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "HCDE530-aviationstack-script/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if "error" in payload:
        raise RuntimeError(f"AviationStack returned an error: {payload['error']}")

    flights = payload.get("data") or []
    if not flights:
        print("No flights in this response — try different query params or check plan limits.")
        return

    # Flatten a handful of nested fields so humans (and CSV tools) can read them easily.
    rows: list[dict[str, object]] = []
    for item in flights:
        dep = item.get("departure") or {}
        arr = item.get("arrival") or {}
        airline = item.get("airline") or {}
        flight = item.get("flight") or {}
        rows.append(
            {
                "flight_date": item.get("flight_date"),
                "flight_status": item.get("flight_status"),
                "airline": airline.get("name"),
                "flight_iata": flight.get("iata"),
                "dep_airport": dep.get("iata"),
                "arr_airport": arr.get("iata"),
            }
        )

    # Print a readable preview to the console.
    print(f"Retrieved {len(rows)} flight records (showing up to 5):\n")
    for row in rows[:5]:
        print(row)

    # Persist everything we flattened so the results open cleanly in a spreadsheet.
    fieldnames = list(rows[0].keys())
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        print("Network error:", exc, file=sys.stderr)
        if "CERTIFICATE_VERIFY_FAILED" in str(exc):
            print(
                "SSL hint: try `/usr/bin/python3` or run macOS "
                "'Install Certificates.command' for your Python build.",
                file=sys.stderr,
            )
        sys.exit(1)
