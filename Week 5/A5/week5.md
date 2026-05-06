# Week 5 — Competency claim: **Data analysis with pandas**

## Claim

I loaded live chat replay data from **four** LEC tournament VODs — **20,985 messages** total across streams `_dE6Hddb8do`, `mPI1-aute0w`, `oxUSw1N9i3k`, and `vUmNslJBba0` — and used pandas to answer five analytical questions about audience behavior. The dataset came from my own collection pipeline (`collect_vod_chat.py`, using yt-dlp) and has columns for timestamp, author channel ID, display name, message text, message type, `super_chat_amount`, and video offset in seconds.

`chat_analysis.py` discovers every `csv/chat_*.csv`, concatenates into one dataframe with a `stream_id` column, and sets the **primary** stream for Q1–Q3 to whichever VOD has the **longest** timeline (`max(video_offset_sec)` per stream, then take the argmax). With the four files currently in `csv/`, that primary is **`vUmNslJBba0`** (7,971 messages). Q4 and Q5 always aggregate across **all** streams present in the folder.

**Methods (pandas practices I used):** load with `read_csv(..., parse_dates=["timestamp"])` so time math is reliable; `pd.concat` to stack streams; `df.head()` / `df.info()` before analysis; `isnull().sum()` to audit gaps; `groupby` for bins and stream summaries; `value_counts()` for authors and tokens; boolean indexing for activity slices. Those steps match what the script prints and keeps the analysis inspectable line by line.

**Why I chose this dataset:** I selected these VODs because the LEC is a tournament for a game (League of Legends) I already know, which helps me interpret chat vocabulary. I kept one league for consistency. I chose LEC specifically because the broadcast chat is primarily English, which fits the stopword list and qualitative reading I used for Q5.

**What I found, with specific numbers (current four-stream run):**

For **Q1**, I grouped the primary stream by 5-minute windows using `groupby` and counted messages per bin. Activity is uneven across a long broadcast: many windows sit near a modest baseline, while a late segment spikes sharply — e.g. **385–390 minutes** into the primary VOD had **239** messages in one window versus a median of about **79** messages per window across the whole stream. That shape suggests bursts tied to in-game or narrative moments rather than flat, steady chatter.

For **Q2**, I used `value_counts()` on `author_channel_id`. There were **1,187** unique chatters on the primary stream; the top poster sent **307** messages. The busiest **10%** (**119** users) accounted for **65.4%** of all messages — strong concentration, consistent with a dedicated core of repeat chatters and many one-off or low-volume viewers.

For **Q3**, I compared Super Chat rate between high- and low-activity windows (`groupby` on `activity_level`). Both rates were **0.0%**. `isnull().sum()` showed **`super_chat_amount` is null for every row** — not a broken formula, but an empty column on this channel. That implies Super Chats are disabled or absent on this tournament broadcast, so money-based engagement is not visible here; a different channel type would be needed to study paid chat.

For **Q4**, I used `groupby` on `stream_id` with aggregated duration (`max(video_offset_sec) / 60`) and divided total messages by duration for **messages per minute** — a length-normalized comparison across four streams of different runtimes:

| `stream_id`   | Total messages | Duration (min) | msg/min |
|---------------|----------------|----------------|---------|
| `vUmNslJBba0` | 7,971          | ~467           | **17.1** |
| `oxUSw1N9i3k` | 5,951          | ~408           | 14.6    |
| `mPI1-aute0w` | 3,625          | ~307           | 11.8    |
| `_dE6Hddb8do` | 3,438          | ~339           | 10.1    |

Higher msg/min can reflect match drama, audience size, time zone, or spam patterns — I treat it as descriptive, not proof of a single cause without external match metadata.

For **Q5**, I split message text on whitespace, removed stopwords, and ran `value_counts()` across **all** streams. Examples from the latest run: **`fnc`** (1,008), **`no`** (952), **`game`** (882), **`lol`** (612), **`good`** (545), **`gg`** (541), **`kc`** (537), **`lec`** (532), **`win`** (497), **`why`** (455). Team and league shorthand plus reaction words surface what the crowd cared about; **`upset`** still appears often (279 in this run), which flags narrative surprise in at least some of these matches. Exact ranks shift slightly if VODs are added or removed.

**Why these operations:** Checking **missing values before** inferential-style summaries avoided chasing a fake Super Chat signal. **`groupby` on video offset** aligns bins to stream start so different start times do not distort within-VOD timing. **Word-level `value_counts()`** pulls signal out of noisy full sentences better than counting whole messages alone.

**Limitations (what this analysis does not claim):** Simple word splitting misses emotes-only messages (some rows have empty `message_text`), does not stem lemmatize team names, and English stopwords may mis-handle mixed-language snippets. Msg/min differences are **not** causal claims about match quality without pairing to esports results. Author IDs are persistent identifiers; I treat them as analytic keys for participation stats, not as invitations to identify individuals.

**Evidence in this folder:** `chat_analysis.py` (five questions, commented operations), `collect_vod_chat.py` (yt-dlp pipeline), **four** CSVs under `csv/`, raw replay JSON under `json/` when the collector is run.

---

## Additional work: reproducibility and script behavior

**Problem:** An earlier version of `chat_analysis.py` used a **hardcoded dictionary** of three video IDs. After a fourth VOD was collected, its CSV sat in `csv/` but was never loaded.

**Fix:** The script **discovers** every file matching `csv/chat_<VIDEO_ID>.csv` (same naming as `collect_vod_chat.py`), concatenates them, and chooses the **primary** dataframe for Q1–Q3 by **maximum** `video_offset_sec` (longest broadcast), not a fixed ID.

**Environment:** `requirements.txt` in `A5/` lists `pandas`, `google-api-python-client`, and `yt-dlp`; a local `.venv` is gitignored; Week 5 `README.md` documents `python3 -m venv .venv` and `pip install -r requirements.txt`. `collect_chat.py` (live YouTube Data API chat) needs `YOUTUBE_API_KEY` in `A5/.env` and only works while a stream is **live**; for finished VODs I use `collect_vod_chat.py`.
