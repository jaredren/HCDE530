"""
Add relative-time columns to chat CSVs for cross-stream comparison.

Each VOD has a different length; raw video_offset_sec is hard to compare across
files. This script writes a parallel dataset under csv/relative/ with:

  stream_id          — video id parsed from filename chat_<id>.csv
  duration_sec       — max(video_offset_sec) for that file (proxy for VOD length)
  relative_time      — video_offset_sec / duration_sec, in [0, 1]
  rel_time_pct       — same as percent through the stream (0–100)
  rel_bin_20         — integer bin 0..19 (20 equal windows of 5% progress each)
  rel_bin_label      — human-readable window, e.g. "0-5%", "95-100%"

Input defaults to csv/coded/ (sentiment-enriched exports). You can point at
csv/raw/ if those files include video_offset_sec.

Usage:
  python3 add_relative_time.py              # all chat_*.csv in csv/coded/
  python3 add_relative_time.py <video_id>   # single file chat_<id>.csv
  python3 add_relative_time.py --input raw  # use csv/raw/ instead
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
CSV_CODED = HERE / "csv" / "coded"
CSV_RAW = HERE / "csv" / "raw"
CSV_RELATIVE = HERE / "csv" / "relative"

N_BINS = 20


def stream_id_from_path(path: Path) -> str:
    stem = path.stem
    if not stem.startswith("chat_"):
        raise ValueError(f"Expected filename chat_<id>.csv, got {path.name}")
    return stem.removeprefix("chat_")


def add_relative_columns(df: pd.DataFrame, stream: str, duration_sec: float) -> pd.DataFrame:
    """Return df with new columns; does not mutate input."""
    out = df.copy()
    out.insert(0, "stream_id", stream)
    out["duration_sec"] = duration_sec

    if duration_sec <= 0:
        out["relative_time"] = 0.0
    else:
        out["relative_time"] = out["video_offset_sec"] / duration_sec
        out["relative_time"] = out["relative_time"].clip(0.0, 1.0)

    out["rel_time_pct"] = out["relative_time"] * 100.0

    # Map [0, 1] into 20 bins; put t==1.0 in the last bin
    idx = (out["relative_time"] * N_BINS).astype(int)
    idx = idx.clip(upper=N_BINS - 1)
    out["rel_bin_20"] = idx
    out["rel_bin_label"] = idx.map(
        lambda i: f"{100 * i / N_BINS:.0f}-{100 * (i + 1) / N_BINS:.0f}%"
    )
    return out


def process_one_csv(src: Path, dest: Path) -> None:
    if "video_offset_sec" not in pd.read_csv(src, nrows=0).columns:
        raise ValueError(f"{src} has no video_offset_sec column")

    df = pd.read_csv(src)
    stream = stream_id_from_path(src)
    duration_sec = float(df["video_offset_sec"].max())

    enriched = add_relative_columns(df, stream, duration_sec)
    dest.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(dest, index=False, encoding="utf-8")


def discover_chat_csvs(directory: Path) -> list[Path]:
    return sorted(directory.glob("chat_*.csv"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write csv/relative/chat_*.csv with relative-time fields."
    )
    parser.add_argument(
        "video_id",
        nargs="?",
        help="Optional: process only chat_<video_id>.csv (e.g. oxUSw1N9i3k or _dE6Hddb8do)",
    )
    parser.add_argument(
        "--input",
        choices=("coded", "raw"),
        default="coded",
        help="Which folder under csv/ to read (default: coded)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=CSV_RELATIVE,
        help=f"Output directory (default: {CSV_RELATIVE})",
    )
    args = parser.parse_args()

    input_dir = CSV_CODED if args.input == "coded" else CSV_RAW

    if args.video_id:
        vid = args.video_id
        if not vid.startswith("chat_"):
            src = input_dir / f"chat_{vid}.csv"
        else:
            src = input_dir / vid
        if not src.exists():
            print(f"Not found: {src}", file=sys.stderr)
            sys.exit(1)
        paths = [src]
    else:
        paths = discover_chat_csvs(input_dir)
        if not paths:
            print(f"No chat_*.csv in {input_dir}", file=sys.stderr)
            sys.exit(1)

    out_dir = args.output
    for src in paths:
        dest = out_dir / src.name
        process_one_csv(src, dest)
        rel = dest.relative_to(HERE) if dest.is_relative_to(HERE) else dest
        print(f"Wrote {rel}")


if __name__ == "__main__":
    main()
