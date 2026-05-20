"""
Collect YouTube live chat replay from a VOD and save it as a clean CSV.

Uses yt-dlp under the hood (more reliable than chat-downloader because
yt-dlp is actively maintained and handles YouTube's frequent page changes).

Usage:
    python3 collect_vod_chat.py VIDEO_URL_OR_ID

Examples:
    python3 collect_vod_chat.py https://www.youtube.com/watch?v=oxUSw1N9i3k
    python3 collect_vod_chat.py oxUSw1N9i3k

Requirements:
    pip install yt-dlp

Outputs:
    json/chat_<video_id>.live_chat.json  — raw yt-dlp replay (unchanged)
    csv/raw/chat_<video_id>.csv          — parsed messages only (no sentiment)
    csv/coded/chat_<video_id>.csv       — same rows + message_sentiment, message_summary

Pipeline: JSON → parse rows → write csv/raw/ → enrich_chat_csv enriches → csv/coded/.

Raw CSV columns (no sentiment):
    timestamp, author_channel_id, display_name, message_text, message_type,
    super_chat_amount, video_offset_sec

Coded CSV adds:
    message_sentiment  — rule-based label from message_coding.py
    message_summary    — short coded summary of the message
"""

import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from enrich_chat_csv import enrich_raw_csv_file

HERE = Path(__file__).resolve().parent
JSON_DIR = HERE / "json"
CSV_RAW_DIR = HERE / "csv" / "raw"
CSV_CODED_DIR = HERE / "csv" / "coded"


def extract_video_id(raw: str) -> str:
    """Pull the bare video ID out of a URL or return as-is if already bare."""
    if "v=" in raw:
        return raw.split("v=")[1].split("&")[0]
    if "youtu.be/" in raw:
        return raw.split("youtu.be/")[1].split("?")[0]
    return raw.strip()


def download_raw_chat(video_id: str, out_dir: Path) -> Path:
    """
    Shell out to yt-dlp to download the live chat replay as a .live_chat.json file.

    yt-dlp writes one JSON object per line. Each object represents one chat action
    (a message, a Super Chat, a membership notification, etc.).
    """
    output_template = str(out_dir / f"chat_{video_id}")
    cmd = [
        "python3", "-m", "yt_dlp",
        "--skip-download",          # we only want the chat, not the video
        "--write-subs",
        "--sub-lang", "live_chat",
        "--output", output_template,
        "--quiet",
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    print(f"Downloading chat replay for {video_id}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    json_path = out_dir / f"chat_{video_id}.live_chat.json"
    if not json_path.exists():
        # yt-dlp error output goes to stderr
        print("yt-dlp output:", result.stderr[:500] if result.stderr else "(none)")
        raise FileNotFoundError(
            f"Chat file not created. The video may not have chat replay enabled,\n"
            f"or yt-dlp couldn't find live_chat subtitles for {video_id}."
        )

    size_kb = json_path.stat().st_size // 1024
    rel = json_path.relative_to(HERE) if json_path.is_relative_to(HERE) else json_path
    print(f"  Raw chat file: {rel} ({size_kb} KB)")
    return json_path


def parse_text(runs: list) -> str:
    """YouTube stores message text as a list of 'runs' — join them into one string."""
    return "".join(run.get("text", "") for run in runs)


def parse_chat_json(json_path: Path) -> list[dict]:
    """
    Parse yt-dlp's .live_chat.json format into clean row dicts (no sentiment fields).

    Renderer types we handle:
        liveChatTextMessageRenderer  — normal chat message
        liveChatPaidMessageRenderer  — Super Chat (paid)
    Everything else (memberships, system notices) is skipped.
    """
    rows = []

    with json_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            replay = obj.get("replayChatItemAction", {})
            offset_ms = int(replay.get("videoOffsetTimeMsec", 0) or 0)
            offset_sec = offset_ms / 1000

            for action in replay.get("actions", []):
                item = action.get("addChatItemAction", {}).get("item", {})

                renderer = item.get("liveChatTextMessageRenderer")
                if renderer:
                    ts_usec = int(renderer.get("timestampUsec", 0) or 0)
                    ts_dt = datetime.fromtimestamp(ts_usec / 1_000_000, tz=timezone.utc)
                    message_text = parse_text(renderer.get("message", {}).get("runs", []))
                    rows.append({
                        "timestamp": ts_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                        "author_channel_id": renderer.get("authorExternalChannelId", ""),
                        "display_name": renderer.get("authorName", {}).get("simpleText", ""),
                        "message_text": message_text,
                        "message_type": "textMessageEvent",
                        "super_chat_amount": "",
                        "video_offset_sec": offset_sec,
                    })
                    continue

                renderer = item.get("liveChatPaidMessageRenderer")
                if renderer:
                    ts_usec = int(renderer.get("timestampUsec", 0) or 0)
                    ts_dt = datetime.fromtimestamp(ts_usec / 1_000_000, tz=timezone.utc)
                    amount = renderer.get("purchaseAmountText", {}).get("simpleText", "")
                    message_text = parse_text(renderer.get("message", {}).get("runs", []))
                    rows.append({
                        "timestamp": ts_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                        "author_channel_id": renderer.get("authorExternalChannelId", ""),
                        "display_name": renderer.get("authorName", {}).get("simpleText", ""),
                        "message_text": message_text,
                        "message_type": "superChatEvent",
                        "super_chat_amount": amount,
                        "video_offset_sec": offset_sec,
                    })

    return rows


def save_csv_raw(rows: list[dict], video_id: str) -> Path:
    """Write messages parsed from replay JSON without sentiment columns."""
    CSV_RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CSV_RAW_DIR / f"chat_{video_id}.csv"
    fieldnames = [
        "timestamp", "author_channel_id", "display_name",
        "message_text", "message_type", "super_chat_amount", "video_offset_sec",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def collect_one(video_id: str) -> Path:
    """
    Download replay JSON, export csv/raw/, run sentiment enrichment → csv/coded/.
    Returns path to the coded CSV.
    """
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    json_path = download_raw_chat(video_id, JSON_DIR)
    rows = parse_chat_json(json_path)

    if not rows:
        raise ValueError(f"No messages parsed from {video_id} — chat replay may be disabled.")

    raw_path = save_csv_raw(rows, video_id)
    coded_path = enrich_raw_csv_file(raw_path, CSV_CODED_DIR / raw_path.name)

    super_chats = sum(1 for r in rows if r["message_type"] == "superChatEvent")
    print(f"  Parsed {len(rows):,} messages ({super_chats} Super Chats)")
    rel_raw = raw_path.relative_to(HERE) if raw_path.is_relative_to(HERE) else raw_path
    rel_coded = coded_path.relative_to(HERE) if coded_path.is_relative_to(HERE) else coded_path
    print(f"  Raw CSV:   {rel_raw}")
    print(f"  Coded CSV: {rel_coded}\n")
    return coded_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 collect_vod_chat.py VIDEO_URL_OR_ID")
        sys.exit(1)

    video_id = extract_video_id(sys.argv[1])
    collect_one(video_id)


if __name__ == "__main__":
    main()
