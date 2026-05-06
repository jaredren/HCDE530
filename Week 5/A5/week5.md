# Week 5 — Competency claim: **Data analysis with pandas**

## Claim

I loaded live chat replay data from **four** LEC tournament VODs — **20,985 messages** total across streams `oxUSw1N9i3k`, `mPI1-aute0w`, `_dE6Hddb8do`, and `vUmNslJBba0` — and used pandas to answer five analytical questions about audience behavior. The dataset came from my own collection pipeline (`collect_vod_chat.py`, using yt-dlp) and has columns for timestamp, author channel ID, display name, message text, message type, and video offset in seconds.

The concrete findings below (Q1–Q3) were written when the **primary** stream for those questions was `oxUSw1N9i3k`. The analysis script was later updated so it automatically loads every `csv/chat_*.csv` file and sets the primary stream to whichever VOD has the **longest** duration (`max(video_offset_sec)`), which after adding the fourth file is `vUmNslJBba0`. Q4 and Q5 always aggregated across **all** streams in the folder, so adding more CSVs updates those results automatically.

**Why I chose this dataset:** I selected these VODs because the LEC is a popular tournament for a game (League of Legends) I am already familiar with, and I wanted consistency in the data, so I stuck to the same game across all of these streams. I chose LEC specifically because it is a primarily English-speaking chat and audience, which better matches the kind of text I wanted to analyze.

**What I actually found, with specific numbers:**

For Q1, I grouped the primary stream (5,951 messages) by 5-minute windows using `groupby` and counted messages per bin. The first hour of the stream was nearly silent — single-digit message counts per window — then chat exploded at the 110–115 minute mark with 232 messages in one 5-minute window. That pattern tells me this was a long match where the decisive moment came very late; you wouldn't see that shape from a short, consistently-paced broadcast.

For Q2, I used `value_counts()` on `author_channel_id` to rank users by message count. The top poster sent 337 messages; most users sent 1–5. The top 10% of chatters (126 out of 1,255 unique users) accounted for 59.6% of all messages in that stream. That level of concentration — more than half the chat coming from a tenth of the audience — is consistent with a core of dedicated esports fans who watch every match, while the majority of viewers either lurk or type once and stop.

For Q3, I filtered to high-activity windows with `df[df["activity_level"] == "high"]` and compared the Super Chat rate between high- and low-activity periods using `groupby`. Both rates came back at exactly 0.0%, which I initially thought was a bug. Checking `isnull().sum()` made it clear: `super_chat_amount` was null for all 5,951 rows, meaning Super Chats are disabled on the LEC tournament broadcast channel — a deliberate platform policy, not a data collection failure. That finding is more useful than a correlation would have been: it tells me that if I want to study monetary engagement in esports chat, I need to look at individual streamer channels, not org-owned tournament broadcasts.

For Q4, I used `groupby` on `stream_id` with a lambda to compute `max(video_offset_sec) / 60` as duration, then divided total messages by duration to get messages per minute — a fairer cross-stream comparison than raw count, since a longer stream naturally accumulates more messages. Stream `oxUSw1N9i3k` came out at 14.6 msg/min versus 11.8 and 10.1 for the other two. That gap might reflect a closer or more dramatic match, a bigger audience, or that broadcast's timing — worth cross-referencing with actual match results in the writeup.

For Q5, I exploded all message text into individual words, filtered out stopwords, and ran `value_counts()` across **all** streams in the dataset. The top results were `fnc` (548), `game` (518), `lol` (415), `gg` (364), `lec` (333), `vit` (216), and `upset` (214). The team abbreviations (FNC = Fnatic, VIT = Vitality) tell me which teams were being talked about most. The word `upset` appearing 214 times suggests at least one of these matches had a result that surprised the audience — that's the kind of qualitative signal that wouldn't appear in message volume data alone. (Exact ranking and counts shift slightly if you add or remove VODs.)

**Why I chose these operations:**

`isnull().sum()` came before any calculations, not after — catching the all-null `super_chat_amount` early meant I didn't spend time building a Super Chat rate analysis on a column that was going to return 0% regardless of how I sliced it. `groupby` with `video_offset_sec` was a deliberate choice over grouping by wall-clock timestamp because streams started at different times; offsetting from stream start makes the bins comparable across broadcasts. `value_counts()` on words rather than full messages gave me vocabulary-level signal that per-message analysis would have buried.

**Evidence in this folder:** `chat_analysis.py` (all five operations, five questions answered with inline comments), `collect_vod_chat.py` (yt-dlp collection pipeline), and **four** CSV files under `csv/` (`chat_oxUSw1N9i3k.csv`, `chat_mPI1-aute0w.csv`, `chat__dE6Hddb8do.csv`, `chat_vUmNslJBba0.csv`) containing the real collected data. Raw replay JSON from yt-dlp lives under `json/` when you run the collector.

---

## Additional work: reproducibility and script behavior

**Problem:** The first version of `chat_analysis.py` used a **hardcoded dictionary** of three video IDs. After I processed a fourth VOD, the new CSV sat in `csv/` but the analysis never included it—only the three named IDs were read.

**Fix:** The script now **discovers** every file matching `csv/chat_<VIDEO_ID>.csv` (same naming convention as `collect_vod_chat.py`) and concatenates them into one dataframe with a `stream_id` column. The **primary** dataframe used for Q1–Q3 is the stream with the **maximum** `video_offset_sec` (longest broadcast), instead of a fixed ID.

**Environment:** I added `requirements.txt` in `A5/` listing `pandas`, `google-api-python-client`, and `yt-dlp`, created a local `.venv` (gitignored), and documented setup in the Week 5 `README.md` (`python3 -m venv .venv`, `pip install -r requirements.txt`). That makes `chat_analysis.py` and the collectors runnable on a fresh machine without guessing packages. `collect_chat.py` (live chat via the YouTube Data API) needs `YOUTUBE_API_KEY` in `A5/.env` and only works while a stream is **live**; for finished VODs I rely on `collect_vod_chat.py` instead.
