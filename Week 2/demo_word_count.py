"""Word-count summary for each row in a survey CSV.

Reads ``demo_responses.csv`` from this script's folder (so it runs correctly
no matter which directory you launch Python from), prints an aligned table,
then aggregate stats over the same counts shown in that table.

Run from anywhere::

    python demo_word_count.py
"""

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "demo_responses.csv"

responses = []

# DictReader: each row is a dict keyed by column name (readable for non-authors of the file).
# newline="" is what the csv module expects so quoted cells with line breaks parse correctly.
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        responses.append(row)


def count_words(response):
    """Rough word count: split on whitespace.

    Chosen for transparency in a learning example. A tokenizer or NLP library
    would be more accurate for real analysis (e.g. contractions, hyphenation).
    """
    return len(response.split())


print(f"{'ID':<6} {'Role':<22} {'Words':<6} {'Response (first 60 chars)'}")
print("-" * 75)

word_counts = []

for row in responses:
    participant = row["participant_id"]
    role = row["role"]
    response = row["response"]

    count = count_words(response)
    word_counts.append(count)

    # Short preview keeps each printed row to a predictable width in the terminal.
    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    print(f"{participant:<6} {role:<22} {count:<6} {preview}")

# Aggregate stats read from ``word_counts`` so the summary matches the table exactly.
print()
print("── Summary ─────────────────────────────────")
print(f"  Total responses : {len(word_counts)}")
print(f"  Shortest        : {min(word_counts)} words")
print(f"  Longest         : {max(word_counts)} words")
print(f"  Average         : {sum(word_counts) / len(word_counts):.1f} words")
