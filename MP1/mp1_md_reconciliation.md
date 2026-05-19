# mp1.md ↔ week6.md reconciliation

**Sources:** `MP1/mp1.md` (scaffold, not submitted) vs `Week 6/week6.md` (competency prose)  
**Numeric ground truth:** `MP1/verification_report.md` (recomputed from `MP1/chat_regular/`)  
**Action:** Report only — no edits to `mp1.md`, `week6.md`, or the notebook.

---

## Part A — Claim-by-claim reconciliation

| # | Claim in mp1.md | Corresponding week6.md | Flag | Notes |
|---|-----------------|------------------------|------|-------|
| A1 | Project path `MP1/mp1.ipynb` | Refers to `week6_mp1_starter.ipynb` in Week 6 folder | **N/A (different artifact)** | Same analysis lineage; different publish path. Not a numeric conflict. |
| A2 | C5 template example: median **15.8** msg/min, peak **47.8**, top 10% **65.4%**, high-bin **64.5** unique authors | C5: median **15.8**, peak **47.8**, top 10% **65.4%**, busier **64.5** vs quieter **22.6** authors | **MATCH** | Template examples align with week6.md and `verification_report.md`. |
| A3 | C5 operations: `read_csv`/`concat`, `stream_id`, primary = `idxmax` on `max(video_offset_sec)` | C3/C5: four files concatenated; primary by longest `video_offset_sec` | **MATCH** | Same pipeline description. |
| A4 | C5 Q1 ops: `groupby("offset_min_bin_5").size()`, `messages_per_min = count/5`, `to_datetime` UTC, `agg` first/last ts | C5 Q1: same operations named | **MATCH** | |
| A5 | C5 Q2 ops: `dropna` on author, `value_counts`, cumulative share, `ceil(0.10 * n_users)` | C5 Q2: same | **MATCH** | |
| A6 | C5 Q3 ops: global top-10% flag, per-bin `nunique`, median split, `groupby("activity_level").agg` | C5 Q3: same pattern (`groupby().agg`, median split, high/low bins) | **MATCH** | mp1 uses `activity_level`; week6 says “high- and low-activity bins” — same logic. |
| A7 | C5 body: **[TODO]** — no submitted claim yet | C5: full numeric paragraph (20,985 rows, 11 cols, all Q1–Q3 stats) | **INCOMPLETE (mp1)** | mp1.md is scaffold only; week6.md is the filled claim. Numbers in TODO examples match week6 when filled in. |
| A8 | C6 table: **4** PNG files (`q1`, `q2`, `q3a`, `q3b`) | C6: “**three** Plotly Express charts” | **MISMATCH** | See **DECISION REQUIRED** below. |
| A9 | C6: horizontal bar Q1, 2-group bar Q2, split Q3a/Q3b for scale | C6: Chart 1 horizontal top-12; Chart 2 two-bar; Chart 3 “splits into two side-by-side bar charts” | **MATCH (design)** | Design rationale aligns; **count** still conflicts (3 vs 4 Plotly figures). |
| A10 | C6 TODO: separate 3a/3b vs dual axis | C6: incompatible scales → split Chart 3 | **MATCH** | mp1.md encodes the split week6 C6 already justifies in prose. |
| A11 | C7: assumed Super Chat Q3 | C7: original Q3 Super Chat vs activity | **MATCH** | |
| A12 | C7: verbatim pivot quote (LEC / official vs creator streams) | C7: same pivot narrative | **MATCH** | Wording in mp1.md matches week6.md intent. |
| A13 | C7 result: `textMessageEvent` only; `super_chat_amount` null; **~64.5** vs **~22.6** authors; heavy share **~65.4%** vs **~68.2%** | C5/C3: zero superChatEvent; C5 Q3: **64.5** / **22.6**, **65.4%** / **68.2%** | **MATCH** | Matches verified recompute (1 dp). |
| A14 | C7 TODO: cite cells for data checks | C3: `value_counts` + `notna().sum()` diagnosis | **INCOMPLETE (mp1)** | week6 already states the checks; mp1.md still TODO. |
| A15 | Artifact map: `MP1/chat_regular/*.csv`, `MP1/images/*.png` | week6: `chat_regular/`, `export_mp1_charts.py` → `mp1_q1_*`, `mp1_q2_*`, `mp1_q3_participation_high_vs_low` | **PARTIAL MISMATCH** | Data path: same four CSVs. **Static export names differ** for Q3 (one dual-panel file in week6 vs `q3a`/`q3b` in MP1 notebook). |
| A16 | mp1.md: four streams in data path (implied) | C3/C5: **four** CSV files; **20,985** rows; **11** columns | **MATCH** | Verified in `verification_report.md`. |
| A17 | mp1.md: primary stream selection rule (no ID named in mp1.md body) | C5 analysis on primary; verification: **`vUmNslJBba0`**, **7,971** rows | **MATCH (implicit)** | mp1.md does not name the ID; week6/verification do. No contradiction. |
| A18 | C5 template: peak at minute **385** (in TODO example) | C5: busiest window **47.8** msg/min (minute 385 in notebook output, not spelled in week6.md C5) | **MATCH** | minute 385 from notebook/verification; not contradicted in week6.md. |
| A19 | C5 template: top 25% / 50% shares | C5: **81.7%** / **91.9%** | **MATCH** | Verified recompute. |
| A20 | C7: exact float **0.6539957345376992** | C7: same float | **MATCH** | Not repeated in mp1.md body (only in week6 C7); no conflict. |

### Summary — mp1.md vs week6.md

| Category | Count |
|----------|-------|
| **MATCH** (numeric/factual alignment) | 15 |
| **MISMATCH** | 1 (chart count: three vs four Plotly outputs) |
| **PARTIAL MISMATCH** | 1 (Q3 static file naming: one dual PNG vs q3a/q3b) |
| **INCOMPLETE (mp1 scaffold)** | 2 (C5/C7 TODO sections — expected) |
| **N/A** | 1 (different notebook path) |

**No numeric mismatch** between mp1.md **example/TODO numbers** and verified week6.md statistics. The substantive conflicts are **documentation structure** (chart count and Q3 export filenames), not recomputed analytics.

---

## Part B — DECISION REQUIRED: 3 vs 4 Plotly charts

### What the notebook actually has

**Plotly chart-producing code:** **one code cell** (notebook cell index **26**). It defines **four** `plotly.express` bar figures and calls **`write_image` + `show()`** four times:

| # | Variable | Title (plot) | PNG export |
|---|----------|--------------|------------|
| 1 | `fig1` | “When was chat fastest? (largest 5-minute slices only)” | `images/mp1_q1_volume_bursts.png` |
| 2 | `fig2` | “Who writes most of the chat on this stream?” | `images/mp1_q2_author_concentration.png` |
| 3 | `fig3a` | “Q3a — In calmer vs busier slices: how many different people chat?” | `images/mp1_q3a_unique_authors.png` |
| 4 | `fig3b` | “Q3b — What share of lines come from the stream's heaviest 10% of posters?” | `images/mp1_q3b_heavy_poster_share.png` |

**What each shows (variables):**

1. **Q1:** Top 12 five-minute windows; x = `messages_per_min`, y = `time_slice` (horizontal bar).
2. **Q2:** Two groups — top 10% busiest accounts vs all others; y = percent of all messages on primary stream.
3. **Q3a:** Quieter vs busier bin halves (median split on messages per window); y = mean unique authors per 5-min bin.
4. **Q3b:** Same split; y = mean percent of lines from stream-wide heaviest 10% of posters.

There are **no other** notebook cells that call `px.bar` / `write_image` for MP1 charts.

### What week6.md C6 states (quoted)

> **Section 4 publishes three Plotly Express charts** in a Jupyter notebook on GitHub, each with code, output, and markdown justification cells.

Same section also says (same paragraph):

> **Chart 3 deliberately splits into two side-by-side bar charts** rather than a single dual-axis chart because the two metrics (counts of unique authors and percentages of lines) have incompatible scales…

### Plain mismatch

| Layer | Count | Notes |
|-------|-------|-------|
| **week6.md C6 headline** | **3** Plotly charts | Explicit sentence above. |
| **week6.md C6 body** | Chart 3 = **2** sub-charts (side-by-side) | Describes Q3 as one “chart” that splits. |
| **MP1/mp1.ipynb** | **4** separate Plotly figures + **4** PNGs | Q3a and Q3b are separate `fig` objects. |
| **week6.md exported figures (matplotlib)** | **3** question-level files | `mp1_q3_participation_high_vs_low` = **one** dual-panel PNG/SVG. |
| **mp1.md C6 table** | **4** PNG filenames | Aligns with notebook, not with “three Plotly charts” headline. |

**DECISION REQUIRED (your call — not resolved here):**

1. Treat the published story as **3 analytical charts** (Q3a+Q3b = one “Chart 3” with two panels) and **rewrite C6 / mp1.md prose** to say so — **or**
2. Treat it as **4 Plotly charts** and **update week6.md C6** “three” → “four” — **or**
3. **Merge Q3a+Q3b** in the notebook to match week6’s three-Plotly / one-dual-panel export model — **or**
4. Keep **4 notebook charts** but cite **week6.md** only for competency narrative and explain the split in Process.

**Do not implement any option until you choose.**

---

## Part C — Notebook integrity (Step 3)

**Run:** Fresh execute of `MP1/mp1.ipynb` from `MP1/` (kernel restart via nbclient, all outputs cleared then re-run).

| Check | Result |
|-------|--------|
| Errors | **None** (completed successfully) |
| Combined shape (load cell) | **(20985, 11)** |
| Primary stream (printed) | **`vUmNslJBba0`** |
| PNGs in `MP1/images/` | **4** files regenerated |

```
mp1_q1_volume_bursts.png      (170,880 bytes)
mp1_q2_author_concentration.png (92,146 bytes)
mp1_q3a_unique_authors.png    (110,840 bytes)
mp1_q3b_heavy_poster_share.png (109,684 bytes)
```

Charts in the notebook match the four PNGs above.

---

## Part D — Git / filesystem directory casing

| Observation | Detail |
|-------------|--------|
| **On disk (this Mac)** | `MP1` and `mp1` resolve to the **same directory** (`realpath` identical). Typical APFS default: **case-insensitive**, `core.ignorecase=true`. |
| **`git status` (untracked)** | Shows `?? MP1/` (capital **MP1**). |
| **Tracked in git today** | **No** `MP1/` or `mp1/` files committed yet — only Week 6 assets such as `Week 6/week6_mp1_starter.ipynb`, `Week 6/mp1_q*.svg`. |
| **Recommendation when you `git add`** | Pick **one canonical casing** (e.g. `MP1/`) and use it consistently in links (`mp1.md` already says `MP1/`). On case-insensitive volumes, `git add mp1` and `git add MP1` target the same tree; on GitHub the first committed spelling becomes the canonical path. |

---

## Part E — Mismatch list (action items for you)

1. **Chart count (C6):** mp1.md lists **4** Plotly PNGs; week6.md C6 says **three** Plotly charts — **DECISION REQUIRED** (Part B).
2. **Q3 export naming:** week6 **matplotlib** export = single `mp1_q3_participation_high_vs_low`; MP1 notebook = **`mp1_q3a_*` + `mp1_q3b_*`** — align naming or cross-reference in prose when you write C6 claim.
3. **mp1.md C5/C7 TODOs:** Still scaffold; week6.md has complete claims — you may **port** verified numbers from week6 into mp1.md when ready (no auto-edit done here).

**No action needed** for recomputed Q1–Q3 statistics: mp1.md TODO examples and week6.md C5/C7 numbers all match `verification_report.md`.

---

## Part F — Post-alignment (2026-05-18): three charts, Q3 two-panel

**Notebook change applied:** `MP1/mp1.ipynb` cell 26 now produces **3** Plotly figures (`fig1`, `fig2`, `fig3` via `make_subplots(1, 2)`). **3** Kaleido PNGs + **3** copied SVGs in `MP1/images/`. Stale `mp1_q3a_*` / `mp1_q3b_*` PNGs removed.

**Verification (Step 4):** Execute from `MP1/` — **zero errors**; **(20985, 11)**; primary **`vUmNslJBba0`**; `images/` = exactly **3** `.png` + **3** `.svg` (no q3a/q3b).

**Git casing:** Still untracked as `?? MP1/`; use **`MP1/`** when you commit.

---

## Part G — `mp1.md` edits for you to apply (DO NOT auto-applied)

### C6 — lines / blocks to change

| Location | Current text (summary) | Change to (your wording) |
|----------|------------------------|---------------------------|
| **Line 29** (strong-claim template) | `For Question [TODO: 1 / 2 / 3a / 3b]` and rationale “split across 3a vs 3b” | **Three charts:** Q1, Q2, Q3. Q3 = **one figure, two subplots** (`make_subplots`, `go.Bar`); left = unique authors, right = heavy-poster %; independent y-axes. |
| **Lines 31–38** (table header + rows) | **Four** rows: q1, q2, **q3a**, **q3b** | **Three** rows. Replace q3a/q3b rows with **one** row: `mp1_q3_participation_high_vs_low.png` \| `make_subplots(1,2)` + `go.Bar` \| left: `avg_different_people` by quieter/busier kind; right: `pct_lines_heavy` (same split) |
| **Line 40** (TODO) | “separate 3a/3b instead of dual axis” | **One chart, two subplots** (incompatible counts vs percentages) — matches `export_mp1_charts.py` / week6.md C6; not four separate Plotly exports |
| **Line 65** (artifact map, optional) | `MP1/images/*.png` | Optional: list three stems or “3 PNG + 3 supplementary SVG” |

### C5 and C7 — still yours to write (not filled by agent)

| Section | Status |
|---------|--------|
| **C5** (lines 11–21) | **Empty scaffold** — `Strong-claim template` + operations list + **TODO** at line 21. Port verified numbers from `week6.md` C5 / `verification_report.md` when you draft. |
| **C7** (lines 44–55) | **Empty scaffold** — pivot table filled except **Result** row TODO (line 53) and closing **TODO** (line 55). Write first-person claims yourself. |

---

## Part H — `week6.md` “three charts” vs residual “four” language

**C6 already says three Plotly charts** — confirmed; no edit needed there.

**“Four” in week6.md that is NOT “four charts” (OK to keep):**

| File | Phrase | Meaning |
|------|--------|---------|
| C3 | “four real-world chat CSV files” | Four VOD exports — **correct** |
| C5 | “20,985-row” combined dataset | Four files concatenated — **correct** |

**Residual “four charts” language — search after notebook align:**

| File | Remaining? |
|------|------------|
| `Week 6/week6.md` | **No** “four Plotly” / “four chart” hits |
| `MP1/mp1.ipynb` | **No** “four charts” / “Four Plotly” in markdown (updated to **three**). “Four CSVs” / “four files” remain where referring to **data files**, not chart count. |
| `MP1/mp1.md` | **Yes — you must edit:** C6 table still lists **4** PNGs (lines 37–38) and template still says **3a/3b** (line 29) |
| `MP1/mp1_md_reconciliation.md` (this file) | Historical sections (Parts B, E) describe **pre-alignment** four-chart state — ignore or archive when done |

---

## Part I — Decision status

| Item | Status |
|------|--------|
| Three charts, Q3 one two-panel figure | **Implemented in notebook** |
| `mp1.md` C6 prose | **Awaiting your edit** (Part G) |
| `mp1.md` C5 / C7 competency claims | **Awaiting your first-person writing** |
