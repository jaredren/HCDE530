import csv
from collections import Counter
from pathlib import Path

def load_rows(csv_filename: str) -> list[dict[str, str]]:
    """
    What it does:
        Loads survey rows from a CSV file in the same folder as this script.
    What it takes:
        csv_filename (str): The CSV file name to open.
    What it returns:
        list[dict[str, str]]: A list of CSV rows as dictionaries.
    """
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / csv_filename

    with csv_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)

def normalize_role(role_value: str) -> str:
    """
    What it does:
        Normalizes a role value and applies an 'Unknown' fallback when empty.
    What it takes:
        role_value (str): The role text from a row.
    What it returns:
        str: A title-cased role label, or 'Unknown' when missing.
    """
    role_raw = (role_value or "").strip()
    return role_raw.title() if role_raw else "Unknown"

def parse_experience(experience_value: str) -> tuple[int | None, str]:
    """
    What it does:
        Parses experience text and classifies it as known, unknown, or incorrect.
    What it takes:
        experience_value (str): The raw experience value from a row.
    What it returns:
        tuple[int | None, str]: (years, status) where years is an integer when known,
        otherwise None, and status is 'known', 'unknown', or 'incorrect'.
    """
    exp_raw = (experience_value or "").strip()
    if exp_raw.isdigit():
        return int(exp_raw), "known"
    if exp_raw == "":
        return None, "unknown"
    return None, "incorrect"

def clean_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    What it does:
        Cleans each survey row for consistent role and experience values.
    What it takes:
        rows (list[dict[str, str]]): Survey row dictionaries loaded from CSV.
    What it returns:
        list[dict[str, str]]: A cleaned list of row dictionaries.
    """
    # Cleaning means: fix role and name text, turn messy experience into either a number
    # or clear labels (Unknown / Incorrect), and add experience_status for each row.
    cleaned_rows: list[dict[str, str]] = []

    # Walk every survey response once; each time we copy the row, update the fields we care
    # about, and save the cleaned copy to the list we will write out later.
    for row in rows:
        cleaned_row = dict(row)
        cleaned_row["role"] = normalize_role(row.get("role", ""))
        cleaned_row["participant_name"] = (
            (row.get("participant_name") or "").strip() or "Unknown"
        )

        # Keep only numeric experience values; label others for data quality visibility.
        years, status = parse_experience(row.get("experience_years", ""))
        if status == "known" and years is not None:
            cleaned_row["experience_years"] = str(years)
            cleaned_row["experience_status"] = "known"
        elif status == "unknown":
            cleaned_row["experience_years"] = "Unknown"
            cleaned_row["experience_status"] = "unknown"
        else:
            cleaned_row["experience_years"] = "Incorrect"
            cleaned_row["experience_status"] = "incorrect"

        # After this row is fixed, add it to the cleaned list and move on to the next person.
        cleaned_rows.append(cleaned_row)

    return cleaned_rows


def write_rows(csv_filename: str, rows: list[dict[str, str]]) -> None:
    """
    What it does:
        Writes row dictionaries to a CSV file in the script folder.
    What it takes:
        csv_filename (str): The output CSV file name.
        rows (list[dict[str, str]]): The rows to write.
    What it returns:
        None.
    """
    if not rows:
        return

    script_dir = Path(__file__).resolve().parent
    output_path = script_dir / csv_filename
    # Column order comes from the first row: same headers as the messy file, plus any new
    # columns we added (for example experience_status) appear in that order too.
    fieldnames = list(rows[0].keys())

    # Write a brand-new CSV: first line is the header row, then one data row per person.
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_data(cleaned_rows: list[dict[str, str]]) -> str:
    """
    What it does:
        Builds a plain-language summary, trend analysis, and text visuals.
    What it takes:
        cleaned_rows (list[dict[str, str]]): Cleaned rows, usually from clean_rows().
    What it returns:
        str: A multi-line summary with dataset stats, trends, and ASCII charts.
    """
    # Scan the cleaned rows to tally roles, tools, missing names, and experience quality for
    # the written summary (each Counter walks the full list once).
    row_count = len(cleaned_rows)
    role_counts = Counter(
        (row.get("role") or "").strip() or "Unknown" for row in cleaned_rows
    )
    unique_roles = sorted(role_counts.keys())
    unknown_name_count = sum(
        1
        for row in cleaned_rows
        if (row.get("participant_name") or "").strip().lower() in {"", "unknown"}
    )
    tool_counts = Counter(
        (row.get("primary_tool") or "").strip() or "Unknown" for row in cleaned_rows
    )
    experience_status_counts = Counter(
        (row.get("experience_status") or "").strip() or "unknown" for row in cleaned_rows
    )

    roles_text = ", ".join(unique_roles) if unique_roles else "none"
    if role_counts:
        most_common_role, most_common_role_count = role_counts.most_common(1)[0]
        most_common_role_text = f"{most_common_role} ({most_common_role_count})"
    else:
        most_common_role_text = "none (0)"

    if tool_counts:
        most_common_tool, most_common_tool_count = tool_counts.most_common(1)[0]
        most_common_tool_text = f"{most_common_tool} ({most_common_tool_count})"
    else:
        most_common_tool_text = "none (0)"

    def build_bar_line(label: str, count: int, max_count: int) -> str:
        """Create a scaled ASCII bar line for one category."""
        bar_length = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "#" * bar_length
        return f"- {label:20} | {bar} ({count})"

    max_role_count = max(role_counts.values()) if role_counts else 0
    role_bar_lines = [
        build_bar_line(role, count, max_role_count)
        for role, count in role_counts.most_common()
    ]

    max_tool_count = max(tool_counts.values()) if tool_counts else 0
    tool_bar_lines = [
        build_bar_line(tool, count, max_tool_count)
        for tool, count in tool_counts.most_common(5)
    ]

    known_experience = experience_status_counts.get("known", 0)
    known_experience_pct = (known_experience / row_count * 100) if row_count else 0

    summary_lines = [
        f"The cleaned dataset has {row_count} rows.",
        f"Unique roles are: {roles_text}.",
        f"There are {unknown_name_count} empty or unknown name fields.",
        "",
        "Trend analysis:",
        f"- Most common role: {most_common_role_text}",
        f"- Most common primary tool: {most_common_tool_text}",
        (
            f"- Experience data quality: {known_experience} known rows "
            f"({known_experience_pct:.1f}%)"
        ),
        "",
        "Role distribution (text chart):",
        *role_bar_lines,
        "",
        "Top tool distribution (text chart):",
        *tool_bar_lines,
    ]

    return "\n".join(summary_lines)


def main() -> None:
    """
    What it does:
        Coordinates loading data, cleaning rows, and writing a new CSV file.
    What it takes:
        None.
    What it returns:
        None.
    """
    rows = load_rows("week3_survey_messy.csv")
    cleaned_rows = clean_rows(rows)
    # Saves week3_survey_cleaned.csv next to this script: full table of cleaned answers.
    write_rows("week3_survey_cleaned.csv", cleaned_rows)
    print(summarize_data(cleaned_rows))

if __name__ == "__main__":
    main()