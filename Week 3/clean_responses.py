"""Clean survey responses and write responses_cleaned.csv."""

import csv
from pathlib import Path


def clean_responses() -> None:
    """Remove rows with empty person identifier and capitalize role values."""
    script_dir = Path(__file__).resolve().parent
    input_path = script_dir / "Previous work" / "demo_responses copy.csv"
    output_path = script_dir / "responses_cleaned.csv"

    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("The CSV file is missing a header row.")

        cleaned_rows = []
        for row in reader:
            # Support either "name" or "participant_id" as the identifier field.
            person_value = (row.get("name") or row.get("participant_id") or "").strip()
            if not person_value:
                continue

            role_value = (row.get("role") or "").upper()
            row["role"] = role_value
            cleaned_rows.append(row)

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)


if __name__ == "__main__":
    clean_responses()
