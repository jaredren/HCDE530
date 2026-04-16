"""Count tool keyword mentions in the response column."""

import csv
import re
from collections import Counter
from pathlib import Path

# Edit this list if you want to track different tools.
TOOL_KEYWORDS = [
    "miro",
    "ai",
    "figma",
    "jira",
    "notion",
    "slack",
]


def count_tool_mentions() -> Counter:
    """Count how often each tool keyword appears in responses."""
    script_dir = Path(__file__).resolve().parent
    input_path = script_dir / "responses_cleaned.csv"

    tool_counts: Counter = Counter()
    tool_patterns = {
        tool: re.compile(rf"\b{re.escape(tool)}\b", re.IGNORECASE)
        for tool in TOOL_KEYWORDS
    }

    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            response_text = row.get("response") or ""
            for tool, pattern in tool_patterns.items():
                matches = pattern.findall(response_text)
                tool_counts[tool] += len(matches)

    return tool_counts


if __name__ == "__main__":
    counts = count_tool_mentions()
    print("Tool mention counts:")
    for tool in TOOL_KEYWORDS:
        print(f"{tool}: {counts[tool]}")
