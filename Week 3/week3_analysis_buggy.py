import csv

# Load the survey data from a CSV file
filename = "week3_survey_messy.csv"
rows = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}

for row in rows:
    role_raw = (row.get("role") or "").strip()
    role = role_raw.title() if role_raw else "Unknown"
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts[role] = 1

print("Responses by role:")
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")

# Calculate the average years of experience
total_experience = 0
valid_experience_count = 0
unknown_experience_count = 0
incorrect_experience_count = 0

# Calculate the average years of experience
for row in rows:
    exp_raw = (row.get("experience_years") or "").strip()
    if exp_raw.isdigit():
        total_experience += int(exp_raw)
        valid_experience_count += 1
    elif exp_raw == "":
        unknown_experience_count += 1
    else:
        # Value exists but is not numeric, so treat it as incorrect data.
        incorrect_experience_count += 1

if valid_experience_count > 0:
    avg_experience = total_experience / valid_experience_count
else:
    avg_experience = 0

print(f"\nKnown experience rows: {valid_experience_count}")
print(f"Unknown experience rows: {unknown_experience_count}")
print(f"Incorrect experience rows: {incorrect_experience_count}")
print(f"Average years of experience: {avg_experience:.1f}")

# Find the top 5 highest satisfaction scores
scored_rows = []
for row in rows:
    score_raw = (row.get("satisfaction_score") or "").strip()
    if score_raw.isdigit():
        scored_rows.append((row.get("participant_name", "Unknown"), int(score_raw)))

scored_rows.sort(key=lambda x: x[1], reverse=True)
top5 = scored_rows[:5]

print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")