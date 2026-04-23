## Week 3 — Debugging messy CSV data

I loaded real survey rows from `week3_survey_messy.csv` (not hardcoded lists), and when the script crashed I treated the traceback as a map: it pointed straight at `int(row["experience_years"])`, so I knew the bug was my assumption that every cell was a clean integer.

The failure was `ValueError: invalid literal for int() with base 10: 'fifteen'`—one person wrote years as a word—so I changed my approach: I validate first, then only sum or store numeric years, and I label anything else as **Incorrect** or **Unknown** instead of forcing `int()` and blowing up the whole run.

After that I split the work into small functions (load → clean → write → summarize), saved a repeatable output file `week3_survey_cleaned.csv`, and printed a short report with role/tool trends and ASCII bars so I could sanity-check the dataset at a glance; I also wrote commits like a debug log so “what broke” and “what I changed” stay visible in history.

### What was actually broken (and what I did about it)

**Experience years.** I was converting the column blindly. Fix: strip the string, accept only digits as “known,” treat empty as unknown, and treat word-y junk like `fifteen` as incorrect data—not a number, not silently dropped.

**Roles and names.** Some rows had empty `role` or missing `participant_name`, which made counts misleading (you’d see a blank category or lose track of who the row was for). Fix: normalize role text and use **Unknown** when a field is empty so the table stays honest.

**“Top” satisfaction (earlier version).** I had sorted ascending and grabbed the first five rows, which would highlight the *lowest* scores. Fix: sort descending so “top five” means what it sounds like.

**Messy editing on my side.** I briefly had duplicated blocks and code outside the loop—classic copy/paste damage—so the script failed before it even got to the real data issues. Fix: refactor into named steps so each bug has an obvious home and I’m not debugging three ideas in one pile.

### Why I added the pieces I did

**Cleaned CSV output.** I wanted something I could open, compare to the messy file, and rerun the same way every time. A print-only script is harder to show as evidence and easier to “lose” mentally.

**`experience_status` plus labels on bad cells.** I didn’t want to pretend bad input was a number; I wanted a visible flag so future me (or a grader) can see *where* the data is messy without rerunning mental archaeology.

**Summary + ASCII charts.** I can’t assume everyone will scroll a CSV, so the text summary is my quick narrative: counts, a couple of “most common” lines with numbers in parentheses, and simple `#` bars—no extra installs, but still a visual-ish read of the shape of the data.

**Commit messages.** I tried to write them like I was narrating a debug session: symptom, diagnosis, fix—because that’s the story I want the history to tell, not a vague “updated files.”
