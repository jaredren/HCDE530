# Week 2 - Competency 2: Code literacy and documentation

## How I define this competency

For me, code literacy and documentation means being able to read a script well enough to explain what it does, change it when needed, and leave clear notes so someone else can follow it. As a UX researcher, that matters because I often collaborate with technical teammates without being a software engineer myself.

In this class, I see four concrete parts of this competency:
- Inline comments that explain why a choice was made
- Docstrings that describe what a function takes, does, and returns
- Commit messages that explain what changed and why
- Markdown documentation that helps a non-technical reader understand the script

## What I worked on this week

This week I focused on understanding `demo_word_count.py`. My goal was not just to run it, but to understand the full flow from CSV file to printed summary. Honestly, I wanted to get to the point where I could explain it out loud without feeling lost.

The hardest part for me was seeing how the pieces connect end to end. I could understand individual lines, but it took longer to connect loading data, looping through rows, counting words, and computing summary statistics as one coherent process.

What helped most was having someone walk through it with me. Once I heard the logic explained in plain language, I could go back to the code and see the structure more clearly. That turned it from "intimidating code" into something I could reason through step by step.

## What I can do now

I now feel confident explaining each major section of the script:
- Data loading with `csv.DictReader`
- The `count_words()` function and its purpose
- The row-by-row loop that creates the output table
- The final summary metrics (total, shortest, longest, average)

The biggest shift is that I can now identify where to edit when requirements change. For example, I can see where to modify the counting rule, where to add another output field, or where to update file handling.

## What good documentation looks like to me

The two most useful documentation pieces for me are:
1. clear run instructions
2. a section-by-section map of what the script does and where changes should happen

As a non-engineer, I need documentation that reduces guesswork. If I can run it and locate the right place to edit, I can participate more confidently in technical work. For me, that confidence is a big part of what progress looks like in this class.

## Evidence I can point to

I can support this competency claim with concrete artifacts:
- Script comments that explain intent (not just mechanics)
- A docstring on `count_words()` describing its purpose and return value
- Markdown reflections and context docs written for a non-technical audience
- Improved understanding of what a strong commit message should include

A strong message is specific about both the problem and the fix. For example:  
"Fixed ValueError: added try/except to skip non-numeric experience_years values."

This is much better than vague messages like "update" or "fix."

## Where I still want to grow

Two areas still feel important for me:
- Reading more complex scripts that are less linear than this one
- Becoming more fluent with Git collaboration workflows (staging, pushing, remote sync, and commit history interpretation)

## Personal takeaway

This week helped me reframe code literacy as sense-making, not memorization. I do not need to be an engineer to contribute; I need to be able to trace how data moves through a script, explain that flow clearly, and document decisions so others can build on the work. I still have a lot to learn, but I can already see that I am more comfortable reading and discussing code than I was at the start of the week.
