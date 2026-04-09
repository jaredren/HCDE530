# Week 2 — Competency 2: Code literacy and documentation

## What I focused on

This week I concentrated on **reading and understanding** `demo_word_count.py`: what it does, how it uses the CSV, and how each part contributes to the printed output.

## What was hardest

The single hardest part was not one line of syntax—it was seeing **how everything connects end to end**: loading the file, turning rows into usable data, counting words, building the table, then computing summary statistics. Until that flow made sense as one story, the script felt like separate puzzle pieces.

## What helped

Having **someone walk me through it** (conversation with a peer, TA, or chat) made the connections click faster than only reading in isolation. Explanation gave me a thread to follow when I went back to the code.

## What I can do now (code literacy)

I can **explain in my own words what each major section does**:

- **Load data**: Open `demo_responses.csv` with UTF-8, use `csv.DictReader` so each row is a dictionary keyed by column names, and collect rows in a list.
- **Define behavior**: `count_words()` splits a response string on whitespace and returns how many tokens that produces (a simple “length of response” metric).
- **Process each row**: Loop participants, read `participant_id`, `role`, and `response`, call `count_words`, store counts, and print a formatted line with a short text preview.
- **Summarize**: Use the list of counts to report total rows, min, max, and average word count.

That mental map is enough that I know **where I would change things** if the assignment asked for different behavior—for example swapping the counting rule, adding another column to the output, or reading a different filename.

## What “good documentation” means to me

For someone with a UX research background (and for future me), the most useful docs are:

1. **How to run it**—clear steps so the script works without guessing the working directory or Python command.
2. **What each section does and where to edit**—so I’m not hunting blindly when requirements change.

Purely internal comments help, but runnable instructions plus a section-by-section walkthrough match how I actually collaborate and learn.

## Where I want to grow next

- **Reading more complex scripts**—beyond a single file with a linear load → loop → print pattern.
- **Git and collaboration workflow**—staging, remotes, pushing, and keeping local and GitHub history aligned so tools like the commit graph stay intelligible.

## Competency 2 takeaway

Code literacy for me is not memorizing syntax; it’s being able to **trace data from file → variables → functions → output**, and pairing that with **documentation that makes the script runnable and changeable** without a software engineering background.
