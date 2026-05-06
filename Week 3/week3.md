## Week 3 — Debugging messy CSV data

I loaded real survey rows from `week3_survey_messy.csv` (not hardcoded lists). When the script crashed, I treated the traceback as a map: it pointed at `int(row["experience_years"])`, so I knew I had assumed every cell was a clean integer.

---

### Bug 1 — `ValueError` on experience years (traceback-led)

**Symptom.** The run stopped with  
`ValueError: invalid literal for int() with base 10: 'fifteen'`.

**What was wrong.** One respondent wrote years as a word. Blind `int(...)` on that cell can never succeed.

**Fix.** Validate before converting: strip the string, treat only all-digit values as known numeric years; treat empty as unknown; treat word-like or junk values as **Incorrect**, not as integers—so the pipeline finishes and the messy cell is visible in output instead of killing the run.

---

### Bug 2 — “Top 5” satisfaction showed the *lowest* scores (logic / sanity-check)

This bug did not show up as a traceback; it showed up as **wrong meaning** in the printed summary.

**What I expected.** A “top five” list by `satisfaction_score` should list the **highest** scores (e.g. 9s and 10s if the scale goes that high).

**What I saw.** The five rows I printed had small satisfaction numbers compared to other rows in the CSV. The label said “top” but the numbers looked like the bottom of the distribution.

**Root cause.** I had sorted the rows **ascending** by score (Python’s default sort order is smallest-to-largest), then took the **first** five rows. That slice is the five **lowest** scores, not the five highest.

**How I verified.** I spot-checked a few `satisfaction_score` values in `week3_survey_messy.csv` against what my script called “top.” The mismatch only made sense once I walked the sort order in my head: first five after ascending sort = minimums.

**Fix.** Sort **descending** by numeric satisfaction (parse scores as integers for ordering), then take the first five rows—or equivalently, sort ascending and take the **last** five. The important part is that the sort direction matches the English word “top.”

---

### Other data-quality fixes (smaller)

**Roles and names.** Empty `role` or missing `participant_name` made counts misleading. I normalized role text and used **Unknown** when a field is empty so tables stay honest.

**Structure.** I briefly had duplicated blocks and code outside the loop from messy editing. Refactoring into small steps (load → clean → write → summarize) gave each bug a clear place to live.

---

### Why I added the pieces I did

**Cleaned CSV output.** I wanted a file I could open, compare to the messy source, and rerun the same way every time—more tangible than print-only output.

**`experience_status` and labels on bad cells.** I did not want to pretend bad input was a number; I wanted a visible flag so anyone can see where the data is messy without re-deriving it from a crash.

**Summary + ASCII charts.** A short text report with counts and `#` bars gives a quick sanity check without extra installs.

---

### Commits and documentation

My main pipeline fix is in commit `071aebd` (“Fix Week 3 survey pipeline: handle messy data and make debugging visible”). That message describes **what the change accomplishes** in general terms; it does not spell out each defect in the one-line subject.

**This write-up** is the detailed record of *what was broken* and *how I knew*. If I had split the work into smaller commits, I would have used **symptom-first** messages so history reads like a debug log, for example:

- `Fix ValueError: experience_years contains 'fifteen', not an integer — parse defensively`
- `Fix satisfaction "top 5": sort scores descending before slice (was ascending, showed lowest)`

Those styles match how I actually diagnosed the issues: traceback text for the first bug, and comparing printed “top” scores to the raw CSV for the second.
