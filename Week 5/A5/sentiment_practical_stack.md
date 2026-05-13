# Practical stack for capturing sentiment (A5 — live chat)

This note describes a **workable path** from what Assignment 5 ships today to sentiment labels that better match real esports chat. It is meant for documentation and planning, not as a requirement to implement everything.

---

## What A5 does today

| Piece | Role |
|--------|------|
| **`message_coding.py`** | `code_message_text()` assigns `message_sentiment` + `message_summary` using **hand-written rules** (keywords, `?`, links, emoji, etc.). |
| **`enrich_chat_csv.py`** | Reads `csv/raw/chat_*.csv`, calls `code_message_text` per row, writes `csv/coded/chat_*.csv`. |
| **`collect_vod_chat.py`** | Downloads replay JSON → raw CSV → optional enrichment → coded CSV. |

Unmatched or vague messages fall through to **generic buckets** (often read as “neutral” / general chat in exports). That is **expected** for rules-only systems: short slang messages rarely hit a strong cue.

---

## Practical stack (recommended order)

### 1. Define the unit of analysis

Decide whether sentiment applies to:

- **every row**, or  
- **human chatter only** (excluding bots, repeated mod messages, bare commands).

**Why:** Bots and `!commands` inflate bland categories and skew aggregates.

**Concrete steps:**

- Filter or tag `message_type` (e.g. separate `superChatEvent` if present).
- Maintain a **small list** of bot channel IDs or `@nightbot`-style authors if you exclude them from “crowd mood.”
- Optionally bucket URLs / score-only lines as **non-stance** (`link_reference`, `score_or_stat`) before modeling mood.

---

### 2. Clean inputs before labeling or modeling

- Strip or separately code **empty / emoji-only / punctuation-only** rows (your coder already branches on these).
- Consider **language**: mixed-language chat may need a detector + separate models per language, or English-only analysis with explicit scope.

---

### 3. Build a **small gold set** (annotation)

- Sample **200–500 messages** stratified by stream or time (not only peak hype windows).
- Use a **short codebook** (roughly **5–8 labels** you can apply consistently), e.g.:  
  hype / frustration / humor / question / neutral / unclear — adjusted to your research questions.

**Why:** You cannot validate “better sentiment” without labels humans agree on.

---

### 4. Choose an estimator (pick one path)

| Path | When it fits | Caveats |
|------|----------------|----------|
| **Keep rules, refine `message_coding.py`** | Course scope stays stdlib-only; you want transparency. | Ceiling is low for sarcasm and domain slang unless lexicons grow large. |
| **Classical ML** (TF‑IDF or char n-grams + logistic regression / linear SVM) | You have labels and want interpretability + no GPU. | Needs labels; weaker on rare slang than transformers. |
| **Pretrained transformer** (multilingual sentiment / emotion) | Quick uplift without training; run locally or via API. | Domain mismatch (“int”, team memes); validate on gold set. |
| **Fine-tune a small model** on your gold (+ augments) | Best fit for **LEC / LoL chat** if you invest time. | Needs consistent labels and compute; document hyperparameters. |

---

### 5. Evaluate honestly

On the **held-out gold** subset:

- Report **accuracy**, **macro F1**, or **confusion matrix** — whatever matches imbalanced classes.
- Compare **new system vs current rules** on the **same rows**.

**Optional:** Only assign a fine-grained label when the model’s **confidence** exceeds a threshold; else **`unclear`** — avoids fake precision.

---

### 6. Integrate with A5 outputs

- **Replace or augment** `code_message_text`: e.g. rules first for cheap buckets, model for ambiguous rows — or one pipeline only, documented.
- Re-run **`enrich_chat_csv.py`** (or a sibling script) so `csv/coded/` stays the single source of truth for notebooks like MP1.

---

### 7. Document limitations (required for good HCI / methods writing)

- Chat is **multi-modal** (emotes, clips context you may not have).
- **Sarcasm** and **spam** break naive polarity.
- Labels reflect **your codebook**, not universal truth.

---

## Summary one-liner

**Clean what you score → annotate a little gold → pick rules vs classical ML vs pretrained/fine-tuned model → evaluate against gold → write outputs back through the same CSV pipeline → disclose limits.**

That stack is **incremental**: you can stop after stricter filtering + refined rules for a smaller project, or extend through supervised learning when you have labels and time.
