# HCDE 530 — Assignment 5

Python scripts and chat data live in the **`A5/`** subfolder (alongside this README).

One-time setup (recommended — installs `pandas`, `google-api-python-client`, and `yt-dlp`):

```bash
cd A5
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the analysis (uses the CSV files already in `csv/`):

```bash
cd A5
source .venv/bin/activate          # if you use the venv above
python3 chat_analysis.py
```

Or without activating the venv: `A5/.venv/bin/python3 chat_analysis.py`.

Collect more VOD chat (requires [yt-dlp](https://github.com/yt-dlp/yt-dlp)):

```bash
cd A5
python3 collect_vod_chat.py VIDEO_ID_OR_URL
```

Outputs go under `A5/json/` (raw replay) and `A5/csv/` (parsed tables). For live-stream collection with `collect_chat.py`, put `.env` containing `YOUTUBE_API_KEY=...` in the same folder as that script (`A5/`).
