# Mini Project 1: Competency claims

**Name:** Jared Ren  
**Project:** `MP1/mp1.ipynb` - YouTube LEC livestream chat analysis  
---

## C5: Data analysis with pandas

> The notebook answers three analytical questions on a 20,985-row, 11-column dataset of YouTube livestream chat messages (four LEC tournament VODs concatenated, with `vUmNslJBba0` selected as the primary stream by `max(video_offset_sec)` rather than hardcoded). Q1 uses `groupby("offset_min_bin_5").size()` on 5-minute time bins of `video_offset_sec`, then divides by 5 to convert to messages per minute, finding that the peak window reaches 47.8 messages per minute (minute 385, 239 messages in bin) against a stream-wide median of 15.8, roughly threefold over baseline. Q2 uses `value_counts()` on `author_channel_id` followed by `cumsum()` on the ranked series to find that the busiest 10% of accounts (about 119 of 1,187 distinct authors) produce 65.4% of all messages, with cumulative shares of 81.7% from the busiest quarter and 91.9% from the busiest half, a heavy-tailed distribution. Q3 combines `groupby().agg()` with multiple named aggregations (size, `nunique`, and mean-of-booleans for the global top-10% indicator), a median split using `np.where()` on bin volume, and a second `groupby()` to compare high- and low-activity bins. Busier windows average 64.5 unique authors per 5-minute bin versus 22.6 in quieter windows, while the heavy-poster line share is 65.4% in busy bins versus 68.2% in quiet ones, meaning louder periods involve broader participation rather than fewer dominant accounts speaking faster. Each question pairs the pandas output with a written interpretation that ties the specific result back to a chat-behavior reading without overclaiming causation; in particular, the analysis cannot attribute bursts to specific in-game events because chat timestamps are not paired with a game event log.


---

## C6: Data visualization

**Strong-claim template:**

> For Question 3 I used `plotly.subplots.make_subplots(rows=1, cols=2)` with two `go.Bar` traces showing mean unique authors (left panel) and mean heavy-poster line share as a percentage (right panel), both split by activity level (quieter vs. busier 5-minute bins). The two-panel structure was the right choice because the two metrics have incompatible y-scales. Unique-author counts run from 22.6 to 64.5, while heavy-poster share is a percentage between roughly 65% and 68%, and putting them on a shared axis would either flatten the percentage difference into invisibility or distort the count comparison. Separate panels keep both readable at their natural scale. The figure is saved as `images/mp1_q3_participation_high_vs_low.png` with the left axis labeled "Average unique authors per 5-minute slice," the right axis labeled "Percent of lines in that slice," and both x-axes labeled "Activity group (median split on messages per 5-min window)."

**Charts in this repo:**

| File | Type | Variables (factual) |
|------|------|---------------------|
| `mp1_q1_volume_bursts.png` | Horizontal `px.bar` | x: `messages_per_min`; y: top 12 `time_slice` windows |
| `mp1_q2_author_concentration.png` | `px.bar` (2 groups) | x: author group; y: percent of all messages |
| `mp1_q3_participation_high_vs_low.png` | `make_subplots(1, 2)` + `go.Bar` | Left: mean unique authors per 5-min bin (quieter vs busier); right: mean % lines from heaviest 10% of posters (same split) |

The clearest readability choice was making Question 1 a horizontal bar chart rather than a vertical one. The time-slice labels for each 5-minute window (e.g., "Minute 385 → 390") are long enough that rotating them under a vertical bar would either truncate them or force a 45-degree tilt that's hard to scan. Horizontal bars put the labels on the left, in left-to-right reading order, with bar length representing rate, so a stakeholder can read the PNG and immediately answer "which windows were busiest, and by how much?" without referring back to the code. I also added an annotation under the chart explaining that the x-axis is messages per minute computed as the bin count divided by five, so the unit is unambiguous from the image alone.

---

## C7: Critical evaluation and professional judgment

> The clearest example of overriding AI-generated output in this project was the Question 3 pivot. My original Q3 asked how Super Chat (paid donation) frequency differed between busy and quiet periods of the stream. When I checked the actual data with `df["message_type"].value_counts()`, every row was a regular text message. Zero paid messages anywhere in the dataset. Rather than report a null finding as if it were meaningful, or quietly drop Q3, I recognized this as a property of the venue: Super Chats are common on individual creator streams (Caedrel and other LoL co-streamers regularly receive them) but rare on official broadcast channels like LEC, which monetize through sponsors and ads instead. I pivoted Q3 to a question the data could actually answer: participation breadth versus heavy-poster dominance in busy versus quiet windows, and documented the pivot in Section 1 so a reader sees what I changed and why.
>
> A second example came during final verification. The notebook picks which of the four streams to analyze using a rule that selects the longest one (`max(video_offset_sec)`). When I was preparing the submission, I ran the analysis against a smaller partial copy of the data and noticed it picked a different primary stream than my repo run had, because "longest" depends on which files are present, and a missing or truncated file would silently change which stream got analyzed without raising any error. I confirmed the full repo data still resolves to `vUmNslJBba0` and added a print statement in the data-loading cell that reports row counts per stream, so any future run makes data completeness visible on the page rather than hidden in the file system. The conclusion bounds what this analysis can and cannot claim: no in-game causal attribution because chat timestamps aren't paired with a game event log, no paid-engagement analysis because Super Chats are absent from official broadcast pulls, and findings limited to this LEC export rather than denser co-stream venues like Caedrel's channel.


---

## Artifact map

| Item | Path |
|------|------|
| Notebook | `MP1/mp1.ipynb` |
| Data | `MP1/chat_regular/*.csv` |
| Static charts | `MP1/images/` (3 PNG + 3 SVG) |
| Collection script (prior week) | `Week 5/A5/collect_vod_chat.py` |
