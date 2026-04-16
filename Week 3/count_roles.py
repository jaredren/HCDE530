"""Count how many times each role appears in responses_cleaned.csv."""

import csv
from collections import Counter
from pathlib import Path


def count_roles() -> Counter:
    """Read the cleaned CSV and count each role value."""
    script_dir = Path(__file__).resolve().parent
    input_path = script_dir / "responses_cleaned.csv"

    role_counts: Counter = Counter()

    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            role = (row.get("role") or "").strip()
            if role:
                role_counts[role] += 1

    return role_counts


if __name__ == "__main__":
    counts = count_roles()
    print("Role counts:")
    for role, count in counts.most_common():
        print(f"{role}: {count}")
