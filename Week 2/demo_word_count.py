# demo_word_count.py
# This script counts the number of words in each response and prints a summary of the results.
import csv


filename = "demo_responses.csv"
responses = []

# We use DictReader so each row is like a mini phone book: keys are column names (easy to read in code).
# newline="" is what Python’s csv docs ask for so the reader handles line breaks inside cells correctly.
# encoding="utf-8" is a common choice for text files so special characters read correctly.
with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        responses.append(row)


def count_words(response):
    """Rough word count: split on spaces.

    Good enough for a class example. It won’t match a dictionary perfectly (for example,
    “don’t” might count as one chunk), but it is simple and easy to understand.
    """
    return len(response.split())


# Padding the columns so the printed table lines up neatly when you run it in the terminal.
print(f"{'ID':<6} {'Role':<22} {'Words':<6} {'Response (first 60 chars)'}")
print("-" * 75)

word_counts = []

# We already loaded the rows above, so we loop that same list for the table and the numbers at the end.
for row in responses:
    participant = row["participant_id"]
    role = row["role"]
    response = row["response"]

    # A small function keeps “how we count words” in one spot if we want to change it later.
    count = count_words(response)
    word_counts.append(count)

    # Only show the start of long answers so each line of output stays a manageable length.
    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    print(f"{participant:<6} {role:<22} {count:<6} {preview}")

# These stats use the same counts we just collected, so the summary matches the table above.
print()
print("── Summary ─────────────────────────────────")
print(f"  Total responses : {len(word_counts)}")
print(f"  Shortest        : {min(word_counts)} words")
print(f"  Longest         : {max(word_counts)} words")
print(f"  Average         : {sum(word_counts) / len(word_counts):.1f} words")
