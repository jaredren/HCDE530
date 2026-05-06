"""
MP1 YouTube Live Chat Analysis — HCDE 530 A5

Dataset: Live chat replay logs from one or more LEC tournament VODs,
collected via yt-dlp. Each row is one chat message with a timestamp,
stable author channel ID, display name, message text, message type
(textMessageEvent or superChatEvent), and offset in seconds from stream start.

CSV files are read automatically from csv/chat_<VIDEO_ID>.csv (every chat_*.csv present).

Analytical questions answered:
  Q1. When during the stream was chat most active, and how dramatic were the spikes?
  Q2. How concentrated is participation — do a few users dominate the chat?
  Q3. Do Super Chat messages appear at all, and does their rate differ by activity level?
  Q4. Which stream(s) had the most engaged audience per minute?
  Q5. What words appear most often across all streams — what does vocabulary reveal?
"""

from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Load every processed chat CSV and tag each row with its video ID
# ---------------------------------------------------------------------------

CSV_DIR = HERE / "csv"


def discover_streams(csv_dir: Path) -> dict[str, Path]:
    """Build stream_id -> path from csv/chat_<VIDEO_ID>.csv (matches collect_vod_chat output names)."""
    out: dict[str, Path] = {}
    for path in sorted(csv_dir.glob("chat_*.csv")):
        stem = path.stem  # e.g. chat_oxUSw1N9i3k or chat__dE6Hddb8do (leading underscore in ID)
        if stem.startswith("chat_"):
            stream_id = stem.removeprefix("chat_")
            out[stream_id] = path
    return out


STREAMS = discover_streams(CSV_DIR)
if not STREAMS:
    raise FileNotFoundError(f"No chat_*.csv files found in {CSV_DIR}")

frames = []
for stream_id, path in STREAMS.items():
    chunk = pd.read_csv(path, parse_dates=["timestamp"])
    chunk["stream_id"] = stream_id
    frames.append(chunk)

all_df = pd.concat(frames, ignore_index=True)

# Longest broadcast (max offset) is the primary example for single-stream analyses
PRIMARY_STREAM_ID = all_df.groupby("stream_id")["video_offset_sec"].max().idxmax()
df = all_df[all_df["stream_id"] == PRIMARY_STREAM_ID].copy()

print(
    f"Loaded {len(STREAMS)} stream(s): {', '.join(sorted(STREAMS.keys()))}\n"
    f"Primary stream for Q1–Q3 (longest by video offset): {PRIMARY_STREAM_ID}\n"
)

# ===========================================================================
# OPERATION 1 — df.head() and df.info()
# ===========================================================================

# Asking: What does this dataset actually contain — how many rows, what columns,
# and are the data types what we expect?
print(df.head())
# The first five rows show real channel IDs (not display names), ISO timestamps,
# and video_offset_sec, confirming we can do time-based analysis.
# If timestamps showed as strings here instead of datetime64 we would need to reparse.

print()
df.info()
# info() tells us row count and dtype per column.
# Non-null counts reveal which columns have gaps before we start computing anything.
# Seeing 5,951 non-null timestamps but only 5,918 non-null message_text rows
# means 33 messages had no text — likely emoji-only or deleted messages.
print()


# ===========================================================================
# OPERATION 5 — df.isnull().sum()
# ===========================================================================

# Asking: Are there missing values in any column, and which ones?
print("Missing values per column:")
print(df.isnull().sum())
# super_chat_amount is null for every row, which tells us Super Chats are
# disabled on this LEC tournament channel — not a collection error.
# The 33 missing message_text rows are minor and will not affect
# timestamp-based or author-based analyses below.
print()


# ===========================================================================
# Q1 — When during the stream was chat most active?
# OPERATION 4 — df.groupby()['col'].count()
# ===========================================================================

# Convert raw seconds to a 5-minute bucket (e.g. 312 sec → minute 5 bin)
df["offset_min_bin"] = (df["video_offset_sec"] // 300 * 5).astype(int)

# Asking: How many messages fell into each 5-minute window of the broadcast?
volume = (
    df.groupby("offset_min_bin")["author_channel_id"]
    .count()
    .reset_index(name="message_count")
)
print("Messages per 5-minute window:")
print(volume.to_string(index=False))
# A window with a count far above the others marks a moment when many viewers
# reacted at once — likely a clutch play, round win, or surprise upset.
# Low counts in early windows show the audience was small or quiet before
# the match reached a decisive stage.

peak = volume.loc[volume["message_count"].idxmax()]
peak_start = int(peak["offset_min_bin"])
peak_end = peak_start + 5
peak_msgs = int(peak["message_count"])
median_msgs = float(volume["message_count"].median())
print(f"\nPeak 5-minute window: {peak_start}–{peak_end} min — {peak_msgs} messages "
      f"(median window had ~{median_msgs:.0f} messages).")
print()


# ===========================================================================
# Q2 — Do a few users dominate the chat, or is participation spread out?
# OPERATION 2 — df['column'].value_counts()
# ===========================================================================

# Asking: How many messages did each unique author send, ranked from most to least?
author_counts = df["author_channel_id"].value_counts()
print("Messages per author (top 20):")
print(author_counts.head(20))
# If the top few authors have counts in the hundreds while most have 1–2,
# participation is highly skewed — a small group of regulars dominates the chat
# while the majority of viewers lurk or only type once.
# This is typical in dedicated esports communities.

n_users   = len(author_counts)
top_n     = max(1, round(n_users * 0.10))
top_share = author_counts.iloc[:top_n].sum() / len(df)
print(f"\n{n_users} unique chatters. Top 10% ({top_n} users) sent {top_share:.1%} of all messages.")
print()


# ===========================================================================
# Q3 — Do Super Chats appear, and are they more common during exciting moments?
# OPERATION 3 — df[df['column'] > value]   (filter to high-activity windows)
# OPERATION 4 — df.groupby()['col'].mean() (compare Super Chat rate by level)
# ===========================================================================

# Label each 5-min window as high or low activity relative to the median count
median_count  = volume["message_count"].median()
high_bins     = volume.loc[volume["message_count"] > median_count, "offset_min_bin"]
df["activity_level"] = df["offset_min_bin"].isin(high_bins.values).map(
    {True: "high", False: "low"}
)

# Asking: Which messages fall inside the busiest windows of the broadcast?
high_df = df[df["activity_level"] == "high"]
# Filtering to high-activity rows lets us compare the composition of busy
# windows against quiet ones. If Super Chats cluster here it means viewers
# spend money specifically during peak excitement, not at random.
print(f"Messages in high-activity windows: {len(high_df)}")
print(f"Messages in low-activity  windows: {len(df[df['activity_level'] == 'low'])}")

# Asking: What fraction of messages in each activity level are Super Chats?
superchat_rate = (
    df.groupby("activity_level")["message_type"]
    .apply(lambda x: (x == "superChatEvent").mean())
    .rename("superchat_rate")
    .reset_index()
)
print("\nSuper Chat rate by activity level:")
print(superchat_rate.to_string(index=False))
# Both rates are 0.0% because Super Chats are disabled on LEC tournament
# broadcasts — standard policy for org-owned channels to keep broadcasts clean
# and avoid pay-to-interact dynamics during competitive play.
# The method is correct; the finding is that monetization is off, not that the
# data is wrong. The same analysis on an individual streamer's channel would
# likely return non-zero rates that could reveal the correlation.
print()


# ===========================================================================
# Q4 — Which stream had the most engaged audience, controlling for length?
# OPERATION 4 — df.groupby()['col'].mean() (messages per minute per stream)
# ===========================================================================

# Asking: Across all streams, what was the average messages-per-minute rate?
stream_stats = all_df.groupby("stream_id").agg(
    total_messages=("author_channel_id", "count"),
    duration_min=("video_offset_sec", lambda x: x.max() / 60),
).reset_index()
stream_stats["msg_per_min"] = stream_stats["total_messages"] / stream_stats["duration_min"]

print("Cross-stream comparison:")
print(stream_stats.to_string(index=False))
# Raw message count would favor the longest stream unfairly.
# Messages per minute controls for broadcast length so we can compare
# audience engagement fairly. A higher rate suggests closer matches,
# more dramatic moments, or a bigger audience for that particular broadcast.
print()


# ===========================================================================
# Q5 — What words dominate chat? What does vocabulary reveal about the community?
# OPERATION 2 — df['column'].value_counts() (word frequency)
# ===========================================================================

STOPWORDS = {
    "the","a","an","is","it","in","to","of","and","i","you","that","this",
    "for","on","are","at","be","was","with","he","she","they","we","my",
    "your","have","has","not","but","or","so","if","do","did","me","him",
    "his","her","its","by","all","just","like","what","how","will","can",
}

words = (
    all_df["message_text"]
    .dropna()
    .str.lower()
    .str.findall(r"[a-z']+")
    .explode()
)

# Asking: What are the most frequent words across all streams combined,
# after removing common filler words?
word_counts = words[~words.isin(STOPWORDS)].value_counts()
print("Top 30 words across all streams:")
print(word_counts.head(30).to_string())
# High-frequency team abbreviations (fnc = Fnatic, vit = Vitality, lec = LEC league)
# and reaction words (gg, lol, upset) tell us which teams and moments
# viewers were most vocal about. A player's name appearing here means
# chat was reacting to their performance specifically during these broadcasts.
print()

# ---------------------------------------------------------------------------
# Plain-language answers (printed after all operations above)
# ---------------------------------------------------------------------------

best_stream = stream_stats.loc[stream_stats["msg_per_min"].idxmax()]
worst_stream = stream_stats.loc[stream_stats["msg_per_min"].idxmin()]
top_author_msgs = int(author_counts.iloc[0])
low_activity_msgs = len(df[df["activity_level"] == "low"])

sc_high = superchat_rate.loc[
    superchat_rate["activity_level"] == "high", "superchat_rate"
]
sc_low = superchat_rate.loc[
    superchat_rate["activity_level"] == "low", "superchat_rate"
]
sc_high_val = float(sc_high.iloc[0]) if len(sc_high) else 0.0
sc_low_val = float(sc_low.iloc[0]) if len(sc_low) else 0.0

top_words = word_counts.head(10)
top_words_str = ", ".join(f"{w} ({int(c)})" for w, c in top_words.items())

sep = "=" * 72
print(sep)
print("ANSWERS — questions for this dataset")
print(sep)
print()
print("Q1. When during the stream was chat most active, and how dramatic were spikes?")
print(
    f"    Chat peaked between {peak_start} and {peak_end} minutes into the primary "
    f"stream (video {PRIMARY_STREAM_ID}), with {peak_msgs} messages in that 5-minute "
    f"window — much higher than a typical window (median ≈ {median_msgs:.0f} messages)."
)
print()
print("Q2. How concentrated is participation — do a few users dominate the chat?")
print(
    f"    Yes. There were {n_users} unique chatters; the top sender posted "
    f"{top_author_msgs} times. The busiest 10% of users ({top_n} people) "
    f"accounted for {top_share:.1%} of all messages in that stream."
)
print()
print("Q3. Do Super Chat messages appear, and does their rate differ by activity level?")
print(
    f"    Super Chats do not appear in this data: rate is {sc_high_val:.1%} in "
    f"high-activity windows and {sc_low_val:.1%} in low-activity windows "
    f"({len(high_df)} vs {low_activity_msgs} messages). "
    "The super_chat_amount column is empty for every row, consistent with "
    "Super Chats being disabled on this tournament broadcast."
)
print()
print(f"Q4. Which stream had the most engaged audience per minute ({len(STREAMS)} streams)?")
print(
    f"    Highest messages per minute: {best_stream['stream_id']} "
    f"({best_stream['msg_per_min']:.1f} msg/min over "
    f"{best_stream['duration_min']:.0f} min). "
    f"Lowest: {worst_stream['stream_id']} ({worst_stream['msg_per_min']:.1f} msg/min)."
)
print()
print("Q5. What words appear most often — what does vocabulary reveal?")
print(f"    Top 10 words (count): {top_words_str}")
print(
    "    Team tags and league shorthand (e.g. fnc, vit, lec) plus reaction words "
    "(gg, lol) show what viewers talked about most across all collected VODs."
)
print()
print(sep)
