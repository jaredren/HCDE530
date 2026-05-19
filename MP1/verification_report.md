# MP1 verification report

**Generated from:** `MP1/chat_regular/*.csv` only  
**Load logic:** Same as `Week 6/export_mp1_charts.py` — `pd.concat`, derive `stream_id` from filename, primary = `groupby("stream_id")["video_offset_sec"].max().idxmax()`  
**Compared against:** `Week 6/week6.md` (prose numbers treated as untrusted until reconciled)  
**Not edited:** `week6.md`, `mp1.md`, `mp1.ipynb`  
**Rounding rule for % claims:** `week6.md` uses one decimal place; **MATCH (1 dp)** if `round(recomputed, 1)` equals the stated value; **MATCH (exact)** if the prose gives full precision.

---

## Step 1 — Ground truth

| Metric | Value |
|--------|-------|
| CSV files loaded | `chat__dE6Hddb8do.csv`, `chat_mPI1-aute0w.csv`, `chat_oxUSw1N9i3k.csv`, `chat_vUmNslJBba0.csv` |
| Combined row count | **20,985** |
| Combined column count | **11** |
| Columns | `timestamp`, `author_channel_id`, `display_name`, `message_text`, `message_sentiment`, `message_summary`, `message_type`, `super_chat_amount`, `video_offset_sec`, `source_file`, `stream_id` |
| Primary stream ID (resolved) | **`vUmNslJBba0`** |
| Primary stream row count | **7,971** |

**Per-stream row counts (combined load):**

| `stream_id` | Rows |
|-------------|------|
| `_dE6Hddb8do` | 3,438 |
| `mPI1-aute0w` | 3,625 |
| `oxUSw1N9i3k` | 5,951 |
| `vUmNslJBba0` | 7,971 |

---

## Step 2 — Recomputed from scratch (full precision)

**Primary stream:** `vUmNslJBba0` (7,971 messages)

### Q1 — 5-minute bins (`offset_min_bin_5 = (video_offset_sec // 300) * 5`, `messages_per_min = count / 5`)

| Metric | Recomputed value |
|--------|------------------|
| Median messages/min | **15.8** |
| Peak messages/min | **47.8** (bin start minute **385**, **239** messages in bin) |

### Q2 — `author_channel_id` value_counts on primary (after `dropna`; **0** rows dropped)

| Metric | Recomputed value |
|--------|------------------|
| Unique authors | **1,187** |
| Total messages | **7,971** |
| Top 10% user count (`ceil(0.10 * n_users)`) | **119** |
| Top 10% message share | **0.6539957345376992** (**65.3996%**) |
| Cumulative share, top 25% of users | **0.8167105758374106** (**81.6711%**) |
| Cumulative share, top 50% of users | **0.9190816710575838** (**91.9082%**) |

### Q3 — Median split on `messages_in_bin` per 5-minute window (median = **79.0** messages)

Labels: `busier` / `quieter` (notebook: `high` / `low`) — same split, same means.

| Metric | Busier / high bins | Quieter / low bins |
|--------|--------------------|--------------------|
| Bin count | **48** | **46** |
| Mean unique authors per bin | **64.4791666667** | **22.6086956522** |
| Mean share of lines from global top 10% posters | **0.65357** (**65.3570%**) | **0.68174** (**68.1740%**) |

### `message_type` / `super_chat_amount` (combined 20,985 rows)

| Check | Recomputed value |
|-------|------------------|
| `message_type.value_counts()` | **`textMessageEvent` only: 20,985** |
| `super_chat_amount` non-null count | **0** |

---

## Step 3 — Reconciliation: `week6.md` numeric claims vs recomputed

| Location (week6.md) | Claim in week6.md | Recomputed | Flag |
|---------------------|-------------------|------------|------|
| C5 | Dataset **20,985** rows | 20,985 | **MATCH** |
| C5 | **11** columns | 11 | **MATCH** |
| C5 Q1 | Busiest window **47.8** messages/min | 47.8 | **MATCH** |
| C5 Q1 | Median **15.8** messages/min | 15.8 | **MATCH** |
| C5 Q2 | Top 10% of accounts → **65.4%** of messages | 65.3996% → **65.4** at 1 dp | **MATCH (1 dp)** |
| C5 Q2 | Top **25%** cumulative **81.7%** | 81.6711% → **81.7** at 1 dp | **MATCH (1 dp)** |
| C5 Q2 | Top **50%** cumulative **91.9%** | 91.9082% → **91.9** at 1 dp | **MATCH (1 dp)** |
| C5 Q3 | Busier windows **64.5** unique authors (avg) | 64.479… → **64.5** at 1 dp | **MATCH (1 dp)** |
| C5 Q3 | Quieter windows **22.6** unique authors (avg) | 22.609… → **22.6** at 1 dp | **MATCH (1 dp)** |
| C5 Q3 | Heavy-poster line share **65.4%** (busy) vs **68.2%** (quiet) | **65.3570%** vs **68.1740%** → 65.4 / 68.2 at 1 dp | **MATCH (1 dp)** |
| C3 (prose) | **four** chat CSV files | 4 files in `MP1/chat_regular/` | **MATCH** |
| C3 / C5 (implied) | Zero `superChatEvent`; empty Super Chat column | `textMessageEvent` only; `super_chat_amount` non-null **0** | **MATCH** |
| C7 | Q2 share **0.6539957345376992** | 0.6539957345376992 | **MATCH (exact)** |

---

## Step 4 — Mismatches

**No numeric mismatches** between `week6.md` claims (table above) and values recomputed from `MP1/chat_regular/` using the export/notebook analysis logic.

All percentage differences are **rounding to one decimal place** in `week6.md`, not different data or formulas.

### Non-numeric / structural notes (not counted as recomputation mismatches)

These are **not** contradicted by the CSV recompute above, but are worth your review:

| Note | Detail |
|------|--------|
| Chart count (C6) | `week6.md` C6 refers to **three** Plotly charts; current `MP1/mp1.ipynb` has **four** (Q3 split into 3a and 3b). Not a numeric reconciliation issue. |
| `mp1.md` | **Not reconciled in this pass** (per instructions: compare to `week6.md` only). Do not assume `mp1.md` numbers are verified. |
| Other streams | Combined load is 20,985 rows; **Q1–Q3 metrics use primary only** (7,971 rows). `week6.md` C5 describes the full dataset size but Q1–Q3 figures are primary-stream results — consistent with notebook behavior. |

---

## Conclusion for your decision

On **`MP1/chat_regular/` as it exists today**, the quantitative claims in **`week6.md` C5/C7 align with a fresh recompute**. That suggests the **uploaded CSVs are complete relative to those claims**, not that the prose is wrong — unless you expected different files or an older export.

If you believed a claim should differ, specify which row in the reconciliation table you distrust; the full-precision recomputed values in Step 2 are the ground truth from these four files.
