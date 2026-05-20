"""
Add message_sentiment and message_summary to a raw chat CSV by reading message_text.

Use after collect_vod_chat.py (or collect_chat.py) has written csv/raw/….

Can be run as a library or from the command line to batch-enrich every csv/raw/chat_*.csv file.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from message_coding import code_message_text

HERE = Path(__file__).resolve().parent
CSV_RAW_DEFAULT = HERE / "csv" / "raw"
CSV_CODED_DEFAULT = HERE / "csv" / "coded"


def _output_fieldnames(raw_fieldnames: list[str]) -> list[str]:
    """Insert sentiment columns after message_text when possible."""
    fn = [c for c in raw_fieldnames if c not in ("message_sentiment", "message_summary")]
    if "message_text" in fn:
        i = fn.index("message_text") + 1
        fn[i:i] = ["message_sentiment", "message_summary"]
    else:
        fn = fn + ["message_sentiment", "message_summary"]
    return fn


def enrich_raw_csv_file(
    raw_path: Path,
    coded_path: Path | None = None,
) -> Path:
    """
    Read one raw CSV, run code_message_text on each message_text, write coded CSV.

    If coded_path is None, writes to csv/coded/<same filename as raw_path>.
    """
    if coded_path is None:
        coded_path = CSV_CODED_DEFAULT / raw_path.name

    coded_path.parent.mkdir(parents=True, exist_ok=True)

    with raw_path.open(encoding="utf-8", newline="") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise ValueError(f"No header row in {raw_path}")

        out_fields = _output_fieldnames(list(reader.fieldnames))
        rows_out = []

        for row in reader:
            text = row.get("message_text")
            if text is None:
                text = ""
            sentiment, summary = code_message_text(text)
            out = dict(row)
            out["message_sentiment"] = sentiment
            out["message_summary"] = summary
            rows_out.append(out)

    with coded_path.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_out)

    return coded_path


def discover_raw_csvs(raw_dir: Path) -> list[Path]:
    return sorted(raw_dir.glob("chat_*.csv"))


def main() -> None:
    raw_dir = CSV_RAW_DEFAULT
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if arg in ("-h", "--help"):
            print(
                "Usage:\n"
                "  python3 enrich_chat_csv.py              # enrich all csv/raw/chat_*.csv\n"
                "  python3 enrich_chat_csv.py <video_id>     # enrich csv/raw/chat_<id>.csv only"
            )
            sys.exit(0)
        vid = arg
        raw_path = raw_dir / f"chat_{vid}.csv"
        if not raw_path.exists():
            print(f"Not found: {raw_path}", file=sys.stderr)
            sys.exit(1)
        out = enrich_raw_csv_file(raw_path)
        print(f"Wrote {out.relative_to(HERE) if out.is_relative_to(HERE) else out}")
        sys.exit(0)

    paths = discover_raw_csvs(raw_dir)
    if not paths:
        print(f"No chat_*.csv in {raw_dir}", file=sys.stderr)
        sys.exit(1)

    for p in paths:
        out = enrich_raw_csv_file(p)
        rel = out.relative_to(HERE) if out.is_relative_to(HERE) else out
        print(f"Enriched {p.name} -> {rel}")


if __name__ == "__main__":
    main()
