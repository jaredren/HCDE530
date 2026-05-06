"""
Collect YouTube live chat messages via the YouTube Data API v3.

Usage:
    python3 collect_chat.py VIDEO_ID [max_pages]

    VIDEO_ID   — the part after ?v= in the YouTube URL (e.g. dQw4w9WgXcQ)
    max_pages  — optional integer cap on API pages (default 20).
                 Each page costs 5 quota units; the free tier gives 10,000/day.
                 20 pages = 100 units and typically yields 400–1000 messages.

Requires: google-api-python-client
    pip install google-api-python-client

Place your key in a .env file next to this script:
    YOUTUBE_API_KEY=AIza...
"""

import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# google-api-python-client is the official Google client library.
# It handles authentication headers, retries, and response parsing for us.
from googleapiclient.discovery import build

HERE = Path(__file__).resolve().parent
CSV_DIR = HERE / "csv"


def load_env(path: Path) -> None:
    """Read KEY=value lines into os.environ (same pattern as your AviationStack script)."""
    if not path.exists():
        raise FileNotFoundError(f"Missing {path} — create it with YOUTUBE_API_KEY=...")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def get_live_chat_id(youtube, video_id: str) -> str:
    """
    Step 1: Ask the API for the video's metadata.
    The activeLiveChatId field is what we need to request messages.
    If the stream is over, this field may be empty — the script will tell you.
    """
    response = youtube.videos().list(
        part="liveStreamingDetails",
        id=video_id,
    ).execute()

    items = response.get("items", [])
    if not items:
        raise ValueError(f"Video '{video_id}' not found. Check the ID.")

    details = items[0].get("liveStreamingDetails", {})
    chat_id = details.get("activeLiveChatId")

    if not chat_id:
        raise ValueError(
            f"No activeLiveChatId for '{video_id}'.\n"
            "The stream must be currently LIVE (not finished or scheduled)."
        )

    return chat_id


def collect_messages(youtube, chat_id: str, max_pages: int) -> list[dict]:
    """
    Step 2: Page through live chat messages.

    The API returns up to 200 messages per page plus a nextPageToken.
    We keep requesting the next page until we run out of tokens or hit max_pages.
    Each liveChatMessages.list call costs 5 quota units.
    """
    all_rows = []
    page_token = None
    page_num = 0

    while page_num < max_pages:
        # Build the request. partTypes we want: id, snippet, authorDetails.
        request_kwargs = dict(
            liveChatId=chat_id,
            part="id,snippet,authorDetails",
            maxResults=200,  # API maximum per page
        )
        if page_token:
            request_kwargs["pageToken"] = page_token

        response = youtube.liveChatMessages().list(**request_kwargs).execute()
        items = response.get("items", [])

        for item in items:
            snippet       = item.get("snippet", {})
            author        = item.get("authorDetails", {})

            # publishedAt comes back as an ISO 8601 string, e.g. "2025-04-15T18:22:01.000Z"
            timestamp_raw = snippet.get("publishedAt", "")

            # superChatDetails is only present on paid Super Chat messages
            super_chat    = snippet.get("superChatDetails")

            all_rows.append({
                "timestamp":          timestamp_raw,
                "author_channel_id":  author.get("channelId", ""),
                "display_name":       author.get("displayName", ""),
                "message_text":       snippet.get("displayMessage", ""),
                # "textMessageEvent" for normal chat, "superChatEvent" for paid
                "message_type":       snippet.get("type", ""),
                "super_chat_amount":  super_chat.get("amountDisplayString", "") if super_chat else "",
            })

        page_num += 1
        page_token = response.get("nextPageToken")

        print(f"  Page {page_num}: got {len(items)} messages (total so far: {len(all_rows)})")

        if not page_token:
            print("  No more pages — reached end of available messages.")
            break

        # The API recommends waiting pollingIntervalMillis before the next request.
        # Without this, you may get empty pages or hit rate limits.
        wait_ms = response.get("pollingIntervalMillis", 2000)
        time.sleep(wait_ms / 1000)

    return all_rows


def save_csv(rows: list[dict], video_id: str) -> Path:
    """Write collected rows to csv/ with a timestamp so multiple runs don't overwrite."""
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path  = CSV_DIR / f"chat_{video_id}_{timestamp}.csv"

    fieldnames = ["timestamp", "author_channel_id", "display_name",
                  "message_text", "message_type", "super_chat_amount"]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return out_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 collect_chat.py VIDEO_ID [max_pages]")
        print("Example: python3 collect_chat.py dQw4w9WgXcQ 10")
        sys.exit(1)

    video_id  = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    load_env(HERE / ".env")
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("Set YOUTUBE_API_KEY in .env next to this script.", file=sys.stderr)
        sys.exit(1)

    # build() creates a client object that knows the YouTube API's endpoints,
    # parameters, and authentication scheme. "youtube" + "v3" selects the right version.
    youtube = build("youtube", "v3", developerKey=api_key)

    print(f"Looking up live chat ID for video: {video_id}")
    chat_id = get_live_chat_id(youtube, video_id)
    print(f"Found live chat ID: {chat_id}\n")

    print(f"Collecting messages (up to {max_pages} pages)...")
    rows = collect_messages(youtube, chat_id, max_pages)

    if not rows:
        print("No messages collected — the chat may be empty or restricted.")
        sys.exit(0)

    out_path = save_csv(rows, video_id)
    print(f"\nSaved {len(rows)} messages to: {out_path}")
    print("\nFirst 3 rows:")
    for row in rows[:3]:
        print(" ", row)


if __name__ == "__main__":
    main()
