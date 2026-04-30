# Week 4 — Competency claim: **C4 — APIs and Data acquisition**

## Strong claim (my voice)

I went beyond the class reviews API and **integrated AviationStack’s `/v1/flights` endpoint myself**, using their documentation to see which query parameters matter (`access_key`, `limit`, and optional filters like `flight_iata` when I want something narrower). The JSON response is not “flat”: the top level has pagination-style metadata and a **`data` array**, and each flight is a **nested object** (for example `departure`, `arrival`, `airline`, and `flight` each contain their own fields). That structure is powerful for apps, but awkward for quick analysis, so **I chose to flatten a small set of fields**—date, status, airline name, IATA flight code, and departure/arrival airport codes—and **print a preview plus write `aviationstack_flights_sample.csv`**. That decision is basically “what does this endpoint return?” plus “what slice of it do I actually want to reason about this week?”

On the **key-handling** side, I’m treating this like real software hygiene: the access key lives in **`.env` next to my script/notebook**, I load it into `os.environ` without printing it, and the repo’s **`.gitignore` excludes `.env`**, so I never paste secrets into source or ship them to GitHub. I also hit a practical lesson that isn’t always spelled out in API docs: **some HTTP clients get blocked without a sensible `User-Agent`**, and **HTTPS tooling can break on a laptop if certificates aren’t wired up for that Python install**—so “API acquisition” isn’t only parsing JSON; it’s chasing the full request path until bytes actually arrive.

**Evidence in this folder:** `flight_aviationstack.py` (HTTP + JSON + CSV), `flight_aviationstack.ipynb` (same API, exploratory), `.env` (ignored by git), and `aviationstack_flights_sample.csv` (readable output artifact).

## What the endpoint returns (short, concrete)

AviationStack returns **JSON** where the interesting payload is typically **`data`**: a list of flight records. Each record mixes **scalar fields** (like `flight_date`, `flight_status`) with **nested dictionaries** (like `airline.name`, `flight.iata`, `departure.iata`, `arrival.iata`). Errors can also come back as JSON with an **`error`** object rather than a thrown HTTP exception, so checking the shape after `json.loads` is part of “reading the response,” not an extra step.

## What I did with it (why those fields)

I extracted fields that answer a simple question fast: **who is flying, between which airports, on what day, in what state** (`scheduled`, `active`, etc.). Airport IATA codes stay compact; airline names read well in a table. Exporting to CSV makes the same extraction legible to anyone grading on “output you can open,” not just terminal prints.

---

*This claim is tied to artifacts in `Week 4/`; the class demo API work I did for practice lives separately in `Week 4/in_class_work/` so it’s obvious what I chose independently for C4.*
