"""
generate_data.py  -  Stage A, METHOD 2: Python script that writes INSERT statements.

Run (from this folder):   python generate_data.py
Needs:                    pip install faker
Reads:                    ../DataImportFiles/program.csv and scholarship.csv
                          (prices and ids, so invoices / awards stay consistent)
Writes:                   output/insert_generated.sql

Tables filled here (load order): person, employee, student, invoice,
installment, payment, scholarship_award, payslip.
"""
import csv
import random
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from faker import Faker

# ----------------------------- configuration -----------------------------
SEED = 42
TODAY = date(2026, 11, 15)          # no payment / issue date after this day
N_STUDENTS = 10_000                 # person_id 1..10000
N_PURE_EMPLOYEES = 560              # person_id 10001..10560 (employee only)
N_DUAL = 40                         # last 40 students are ALSO employees
N_AWARDS = 3_000
INVOICES_PER_STUDENT = 2
PAY_MONTHS = [(y, m) for y in (2025, 2026) for m in range(1, 13)
              if (y, m) <= (2026, 10)]

HERE = Path(__file__).resolve().parent
CSV_DIR = HERE.parent / "DataImportFiles"
OUT_DIR = HERE / "output"
OUT_DIR.mkdir(exist_ok=True)

random.seed(SEED)
Faker.seed(SEED)
fake = Faker("en_US")


# ------------------------------- helpers ---------------------------------
def q(text):
    """SQL string literal (escapes single quotes)."""
    return "'" + str(text).replace("'", "''") + "'"


def dt(value):
    return "'" + value.isoformat() + "'"


def money(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def add_years(day, years):
    try:
        return day.replace(year=day.year + years)
    except ValueError:                      # 29 Feb
        return day.replace(year=day.year + years, day=28)


def write_table(out, name, columns, rows, batch=1000):
    """Writes multi-row INSERTs, returns the number of rows."""
    cols = ", ".join(columns)
    chunk = []
    for row in rows:
        chunk.append("  (" + ", ".join(row) + ")")
        if len(chunk) == batch:
            out.write(f"INSERT INTO {name} ({cols}) VALUES\n" + ",\n".join(chunk) + ";\n")
            chunk = []
    if chunk:
        out.write(f"INSERT INTO {name} ({cols}) VALUES\n" + ",\n".join(chunk) + ";\n")
    out.write("\n")
    return len(rows)


# --------------------------- read the CSV files ---------------------------
with open(CSV_DIR / "program.csv", encoding="utf-8") as f:
    programs = {int(r["program_id"]): int(Decimal(r["annual_price"]) * 100)
                for r in csv.DictReader(f)}
with open(CSV_DIR / "scholarship.csv", encoding="utf-8") as f:
    scholarship_ids = [int(r["scholarship_id"]) for r in csv.DictReader(f)]
program_ids = list(programs)

counts = {}

# ------------------------------- person ----------------------------------
n_persons = N_STUDENTS + N_PURE_EMPLOYEES
first_dual_id = N_STUDENTS - N_DUAL + 1
national_ids = random.sample(range(100_000_000, 1_000_000_000), n_persons)

birth = {}
person_rows = []
for pid in range(1, n_persons + 1):
    if pid > N_STUDENTS:                       # employee only
        b = rand_date(date(1960, 1, 1), date(1995, 12, 31))
    elif pid >= first_dual_id:                 # student AND employee
        b = rand_date(date(1990, 1, 1), date(1998, 12, 31))
    else:                                      # student only
        b = rand_date(date(1990, 1, 1), date(2005, 12, 31))
    birth[pid] = b
    first, last = fake.first_name(), fake.last_name()
    slug = re.sub(r"[^a-z0-9]", "", f"{first}{last}".lower())
    email = f"{slug}.{pid}@college.example"
    phone = f"05{random.randint(0, 9)}-{random.randint(1000000, 9999999)}"
    person_rows.append([str(pid), q(national_ids[pid - 1]), q(first), q(last),
                        dt(b), q(email), q(phone)])

# ------------------------------- employee --------------------------------
POSITION_WEIGHTS = {1: 14, 2: 12, 3: 6, 4: 35, 5: 10, 6: 8, 7: 6, 8: 9}
SALARY_RANGE = {1: (11000, 18000), 2: (8000, 11000), 3: (10000, 15000),
                4: (14000, 24000), 5: (12000, 20000), 6: (11000, 17000),
                7: (8500, 12000), 8: (8000, 11500)}
employee_ids = list(range(first_dual_id, n_persons + 1))        # 600 employees
employee_rows, base_salary, cashier_pool = [], {}, []
for eid in employee_ids:
    pos = random.choices(list(POSITION_WEIGHTS), list(POSITION_WEIGHTS.values()))[0]
    lo, hi = SALARY_RANGE[pos]
    salary_cents = random.randrange(lo, hi + 1, 50) * 100
    base_salary[eid] = salary_cents
    if pos in (1, 2):
        cashier_pool.append(eid)
    hire = rand_date(max(date(2008, 1, 1), add_years(birth[eid], 22)), date(2024, 12, 31))
    employee_rows.append([str(eid), str(pos), dt(hire), money(salary_cents)])

# ------------------------------- student ---------------------------------
student_rows, enrolled = [], {}
for sid in range(1, N_STUDENTS + 1):
    start = max(date(2020, 9, 1), add_years(birth[sid], 18))
    enr = rand_date(start, date(2026, 10, 1))
    enrolled[sid] = enr
    prog = random.choice(program_ids)
    active = "TRUE" if random.random() < 0.92 else "FALSE"
    student_rows.append([str(sid), str(prog), dt(enr), active])
student_program = {int(r[0]): int(r[1]) for r in student_rows}

# ------------------- invoice / installment / payment ---------------------
invoice_rows, installment_rows, payment_rows = [], [], []
invoice_id = payment_id = 0
for sid in range(1, N_STUDENTS + 1):
    price = programs[student_program[sid]]
    for _ in range(INVOICES_PER_STUDENT):
        invoice_id += 1
        total = (price // 2 // 100) * 100 + random.choice([0, 0, 0, 15000, 25000])
        issue = rand_date(max(enrolled[sid], date(2022, 1, 1)), date(2026, 11, 1))
        due = issue + timedelta(days=random.randint(30, 90))

        # installments (weak entity): equal parts, remainder on the last one
        n_inst = random.choice([2, 3, 3, 4])
        part = total // n_inst
        span = (due - issue).days
        for j in range(1, n_inst + 1):
            amount = part if j < n_inst else total - part * (n_inst - 1)
            deadline = due if j == n_inst else issue + timedelta(days=round(span * j / n_inst))
            installment_rows.append([str(invoice_id), str(j), dt(deadline), money(amount)])

        # payments
        r = random.random()
        pieces = []
        if r < 0.60:                                   # fully paid
            n_pay = random.choice([1, 2, 2, 3])
            if n_pay == 1:
                pieces = [total]
            else:
                cuts = sorted(random.sample(range(100, total, 100), n_pay - 1))
                bounds = [0] + cuts + [total]
                pieces = [bounds[i + 1] - bounds[i] for i in range(n_pay)]
        elif r < 0.80:                                 # partially paid
            part_paid = (total * random.randint(30, 70) // 100 // 100) * 100
            pieces = [min(max(part_paid, 100), total - 100)]
        for amount in pieces:
            payment_id += 1
            pay_date = rand_date(issue, min(due + timedelta(days=20), TODAY))
            method = random.choices([1, 2, 3, 4, 5], [10, 40, 30, 10, 10])[0]
            payment_rows.append([str(payment_id), str(invoice_id), str(method),
                                 str(random.choice(cashier_pool)), dt(pay_date), money(amount)])

        paid = sum(pieces)
        if paid == total:
            status = 3                                  # Paid
        elif paid > 0:
            status = 2                                  # Partially Paid
        else:
            status = 4 if due < TODAY else 1            # Overdue / Pending
        invoice_rows.append([str(invoice_id), str(sid), str(status), dt(issue),
                             dt(due), money(total)])

# --------------------------- scholarship_award ---------------------------
award_rows, seen = [], set()
while len(award_rows) < N_AWARDS:
    sid = random.randint(1, N_STUDENTS)
    sch = random.choice(scholarship_ids)
    day = rand_date(max(enrolled[sid], date(2021, 9, 1)), date(2026, 11, 1))
    if (sid, sch, day) in seen:
        continue
    seen.add((sid, sch, day))
    award_rows.append([str(len(award_rows) + 1), str(sid), str(sch), dt(day)])

# -------------------------------- payslip --------------------------------
payslip_rows = []
for eid in employee_ids:
    for year, month in PAY_MONTHS:
        gross = int(base_salary[eid] * random.uniform(1.00, 1.08))
        deductions = int(gross * random.uniform(0.18, 0.28))
        paid = "NULL" if random.random() < 0.02 else dt(date(year, month, 28))
        payslip_rows.append([str(eid), str(year), str(month), money(gross),
                             money(deductions), paid])

# ------------------------------- write file -------------------------------
with open(OUT_DIR / "insert_generated.sql", "w", encoding="utf-8", newline="\n") as out:
    out.write("-- Generated by generate_data.py (seed %d). Do not edit by hand.\n" % SEED)
    out.write("BEGIN;\n\n")
    counts["person"] = write_table(out, "person",
        ["person_id", "national_id", "first_name", "last_name", "birth_date", "email", "phone"], person_rows)
    counts["employee"] = write_table(out, "employee",
        ["person_id", "position_code", "hire_date", "base_salary"], employee_rows)
    counts["student"] = write_table(out, "student",
        ["person_id", "program_id", "enrollment_date", "is_active"], student_rows)
    counts["invoice"] = write_table(out, "invoice",
        ["invoice_id", "student_id", "status_code", "issue_date", "due_date", "total_amount"], invoice_rows)
    counts["installment"] = write_table(out, "installment",
        ["invoice_id", "installment_number", "deadline_date", "amount"], installment_rows)
    counts["payment"] = write_table(out, "payment",
        ["payment_id", "invoice_id", "method_code", "recorded_by", "payment_date", "amount"], payment_rows)
    counts["scholarship_award"] = write_table(out, "scholarship_award",
        ["award_id", "student_id", "scholarship_id", "award_date"], award_rows)
    counts["payslip"] = write_table(out, "payslip",
        ["employee_id", "pay_year", "pay_month", "gross_salary", "deductions", "paid_date"], payslip_rows)
    out.write("COMMIT;\n")

print("Rows generated:")
for table, n in counts.items():
    print(f"  {table:<18} {n:>7}")
big = [t for t, n in counts.items() if n >= 20_000]
print("Tables with >= 20,000 rows:", big)
assert len(big) >= 2, "need at least 2 tables with 20,000 rows"
assert all(n >= 500 for n in counts.values()), "every table needs >= 500 rows"
print("Written:", OUT_DIR / "insert_generated.sql")
