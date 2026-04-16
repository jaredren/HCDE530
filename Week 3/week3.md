## Week 3 — Debugging messy CSV data

I loaded messy real-world survey data from `week3_survey_messy.csv`, used the traceback to pinpoint the exact failure (`int(row["experience_years"])`), and refactored the script into focused functions so each step (load → clean → write → summarize) was easier to debug.

The script threw `ValueError: invalid literal for int() with base 10: 'fifteen'` because one row had the word “fifteen” in the `experience_years` column, so I fixed the pipeline by treating any non-numeric experience value as **Incorrect** (and missing values as **Unknown**) instead of letting the script crash.

Finally, I wrote the cleaned results to `week3_survey_cleaned.csv` every run and added a summary with counts and ASCII charts to make trends and data-quality issues repeatable and easy to verify, and my commits document the specific bugs I found and the fixes I applied.
