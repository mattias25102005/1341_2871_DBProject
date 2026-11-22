"""
make_csv.py  -  prepares the two CSV files used by METHOD 3 (CSV import).
  program.csv      (500 rows)
  scholarship.csv  (500 rows)
Run:  python make_csv.py
Then import them with the psql copy command (see the README).
You can also generate files with the same columns on mockaroo.com instead.
"""
import csv
import random
from pathlib import Path

random.seed(2026)
HERE = Path(__file__).resolve().parent

FIELDS = [
    "Computer Science", "Software Engineering", "Information Systems", "Data Science",
    "Cyber Security", "Business Administration", "Accounting", "Economics",
    "Marketing", "Law", "Psychology", "Sociology", "Education", "Nursing",
    "Biotechnology", "Electrical Engineering", "Mechanical Engineering",
    "Industrial Engineering", "Architecture", "Graphic Design", "Communications",
    "Political Science", "English Literature", "Mathematics", "Environmental Studies",
]

# ---------- program.csv : 25 fields x 4 levels x 5 tracks = 500 ----------
LEVELS = [("Certificate", 1, 12000), ("Diploma", 2, 16000),
          ("Bachelor", 3, 22000), ("Bachelor Honors", 4, 26000)]
TRACKS = [("Day", 1.00), ("Evening", 0.90), ("Weekend", 0.85),
          ("Online", 0.80), ("Executive", 1.20)]

programs = []
pid = 1
for field in FIELDS:
    for level, years, base in LEVELS:
        for track, factor in TRACKS:
            price = round(base * factor * random.uniform(0.95, 1.05), 2)
            programs.append([pid, f"{level} in {field} ({track})", f"{price:.2f}", years])
            pid += 1

with open(HERE / "program.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["program_id", "name", "annual_price", "duration_years"])
    w.writerows(programs)

# ---------- scholarship.csv : 20 types x 25 fields = 500 ----------
TYPES = {
    "Merit": "Average grade above 90 in the previous academic year",
    "Excellence": "Top 5 percent of the graduating class",
    "Deans List": "Placed on the Dean's list for two consecutive semesters",
    "Need-Based": "Family income below the national average, documents required",
    "Women in STEM": "Female student enrolled in a science or technology program",
    "Military Service": "Completed full military or national service",
    "Community Service": "At least 120 volunteer hours during the last year",
    "Sports": "Competes at national level for a recognized club",
    "Arts": "Portfolio approved by the arts committee",
    "Research": "Participation in a faculty research project",
    "Entrepreneurship": "Business plan approved by the innovation center",
    "Alumni": "Child or sibling of a college graduate",
    "First Generation": "First person in the family to study for a degree",
    "Periphery Student": "Resident of a peripheral town",
    "New Immigrant": "Immigrated within the last five years",
    "Disability Support": "Recognized disability, committee approval required",
    "Presidents": "Selected by the college president office",
    "Innovation": "Winner of the yearly innovation challenge",
    "Leadership": "Elected student union or class representative",
    "Single Parent": "Single parent studying full time",
}
scholarships = []
sid = 1
for stype, criteria in TYPES.items():
    for field in FIELDS:
        amount = random.randrange(1000, 25001, 500)
        scholarships.append([sid, f"{stype} Scholarship - {field}", f"{amount:.2f}", criteria])
        sid += 1

with open(HERE / "scholarship.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["scholarship_id", "name", "amount", "criteria"])
    w.writerows(scholarships)

print(f"program.csv: {len(programs)} rows, scholarship.csv: {len(scholarships)} rows")
