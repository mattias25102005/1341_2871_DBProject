# Data Dictionary – College Accounting Department

**System:** College (מכללה) – **Unit:** Accounting department (אגף חשבונות)
**DBMS:** PostgreSQL 16 (Docker) – 10 system entities + 3 ENUM (key/value) tables.

The accounting department handles two money flows: **money coming in** from students (invoices, installments, payments, scholarships) and **money going out** to the staff (payroll). A single `person` table holds the data common to everyone, and `student` / `employee` specialise it.

## 1. Overview

| # | Table | Kind | Purpose (short) |
|---|-------|------|-----------------|
| 1 | `person` | parent entity | Identity data shared by students and employees |
| 2 | `student` | child of `person` | Student enrollment data |
| 3 | `employee` | child of `person` | Staff employment data |
| 4 | `program` | entity | Study programs and their yearly price |
| 5 | `invoice` | entity | Tuition invoices issued to students |
| 6 | `installment` | **weak entity** (of `invoice`) | Payment schedule of an invoice |
| 7 | `payment` | entity | Money actually received |
| 8 | `scholarship` | entity | Scholarship catalogue |
| 9 | `scholarship_award` | associative entity (M:N) | Which student received which scholarship, and when |
| 10 | `payslip` | **weak entity** (of `employee`) | Monthly salary slip of an employee |
| 11 | `invoice_status` | ENUM | Invoice status values |
| 12 | `payment_method` | ENUM | Payment method values |
| 13 | `job_position` | ENUM | Job titles of employees |

## 2. Relationships

| Relationship | Parent side (1) | Child side (N) | Foreign key | Notes |
|--------------|-----------------|----------------|-------------|-------|
| inheritance | `person` | `student` | `student.person_id` | overlapping: a person can be student **and** employee |
| inheritance | `person` | `employee` | `employee.person_id` | |
| enrolled_in | `program` | `student` | `student.program_id` | |
| receives | `student` | `invoice` | `invoice.student_id` | |
| split_into | `invoice` | `installment` | `installment.invoice_id` | identifying relationship (weak entity) |
| settled_by | `invoice` | `payment` | `payment.invoice_id` | |
| records | `employee` | `payment` | `payment.recorded_by` | the employee who entered the payment |
| earns | `employee` | `payslip` | `payslip.employee_id` | identifying relationship (weak entity) |
| is_awarded | `student` | `scholarship_award` | `scholarship_award.student_id` | M:N with `scholarship` through the associative entity |
| grants | `scholarship` | `scholarship_award` | `scholarship_award.scholarship_id` | |
| has_status | `invoice_status` | `invoice` | `invoice.status_code` | |
| paid_with | `payment_method` | `payment` | `payment.method_code` | |
| holds | `job_position` | `employee` | `employee.position_code` | |

## 3. Tables

### 3.1 `person`
**Purpose:** stores the personal data common to every individual known to the college, so it is not repeated in `student` and `employee`.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `person_id` | int | PK | Internal identifier |
| `national_id` | varchar(9) | NOT NULL, UNIQUE | National ID number |
| `first_name` | varchar(50) | NOT NULL | First name |
| `last_name` | varchar(50) | NOT NULL | Last name |
| `birth_date` | date | NOT NULL, CHECK < 2010-01-01 | Date of birth (everyone must be an adult) |
| `email` | varchar(100) | NOT NULL, UNIQUE | Contact email |
| `phone` | varchar(15) | – | Contact phone (optional) |

**Relations:** parent of `student` and `employee` (1:1 specialisation, a person can have both roles).

### 3.2 `student`
**Purpose:** enrollment data of people who study at the college.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `person_id` | int | PK, FK → `person` | Same identifier as the person (inheritance) |
| `program_id` | int | NOT NULL, FK → `program` | Program the student is enrolled in |
| `enrollment_date` | date | NOT NULL, DEFAULT today | Date of first enrollment |
| `is_active` | boolean | NOT NULL, DEFAULT TRUE | FALSE if the student left or graduated |

**Relations:** is a `person`; studies one `program`; receives many `invoice`s; can receive many `scholarship_award`s.

### 3.3 `employee`
**Purpose:** employment data of the college staff.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `person_id` | int | PK, FK → `person` | Same identifier as the person (inheritance) |
| `position_code` | int | NOT NULL, FK → `job_position` | Job title |
| `hire_date` | date | NOT NULL | Date of hiring |
| `base_salary` | numeric(9,2) | NOT NULL, CHECK > 0 | Monthly base salary |

**Relations:** is a `person`; holds one `job_position`; has many `payslip`s; records many `payment`s.

### 3.4 `program`
**Purpose:** catalogue of study programs (field, level and track) with the yearly tuition used to compute invoices.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `program_id` | int | PK | Identifier |
| `name` | varchar(80) | NOT NULL, UNIQUE | Program name, e.g. "Bachelor in Accounting (Evening)" |
| `annual_price` | numeric(8,2) | NOT NULL, CHECK > 0 | Tuition for one academic year |
| `duration_years` | int | NOT NULL, CHECK 1–6 | Length of the program in years |

**Relations:** one program has many `student`s.

### 3.5 `invoice`
**Purpose:** a tuition invoice issued by the accounting department to a student.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `invoice_id` | int | PK | Identifier |
| `student_id` | int | NOT NULL, FK → `student` | Billed student |
| `status_code` | int | NOT NULL, DEFAULT 1, FK → `invoice_status` | Current status |
| `issue_date` | date | NOT NULL, DEFAULT today | Date the invoice was issued |
| `due_date` | date | NOT NULL, CHECK ≥ `issue_date` | Final date of payment |
| `total_amount` | numeric(9,2) | NOT NULL, CHECK > 0 | Total to pay |

**Relations:** belongs to one `student`; has one `invoice_status`; is split into many `installment`s; is settled by many `payment`s.

### 3.6 `installment` (weak entity)
**Purpose:** one slice of the payment schedule of an invoice. It cannot exist without its invoice, so it is identified by the invoice key plus its own number.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `invoice_id` | int | PK (part), FK → `invoice`, ON DELETE CASCADE | Owning invoice |
| `installment_number` | int | PK (part), CHECK > 0 | Order of the installment inside the invoice (1, 2, 3…) |
| `deadline_date` | date | NOT NULL | Date this slice must be paid |
| `amount` | numeric(9,2) | NOT NULL, CHECK > 0 | Amount of this slice |

**Relations:** belongs to exactly one `invoice`. The installments of an invoice add up to its `total_amount`.

### 3.7 `payment`
**Purpose:** a real payment received from a student for an invoice, entered by an accounting employee.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `payment_id` | int | PK | Identifier |
| `invoice_id` | int | NOT NULL, FK → `invoice` | Invoice being paid |
| `method_code` | int | NOT NULL, FK → `payment_method` | How the money was paid |
| `recorded_by` | int | NOT NULL, FK → `employee` | Employee who entered the payment |
| `payment_date` | date | NOT NULL, DEFAULT today | Date the money was received |
| `amount` | numeric(9,2) | NOT NULL, CHECK > 0 | Amount received |

**Relations:** belongs to one `invoice`; uses one `payment_method`; recorded by one `employee`. An invoice can be paid in several payments.

### 3.8 `scholarship`
**Purpose:** catalogue of the scholarships the college can grant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `scholarship_id` | int | PK | Identifier |
| `name` | varchar(80) | NOT NULL, UNIQUE | Scholarship name |
| `amount` | numeric(8,2) | NOT NULL, CHECK > 0 | Value of the scholarship |
| `criteria` | varchar(200) | – | Eligibility conditions |

**Relations:** granted many times through `scholarship_award`.

### 3.9 `scholarship_award` (associative entity)
**Purpose:** resolves the M:N relationship between students and scholarships. It has its own key so the **same scholarship can be awarded to the same student in different years**.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `award_id` | int | PK | Identifier |
| `student_id` | int | NOT NULL, FK → `student` | Student who received the scholarship |
| `scholarship_id` | int | NOT NULL, FK → `scholarship` | Scholarship received |
| `award_date` | date | NOT NULL, DEFAULT today | Date of the award |
| – | – | UNIQUE (`student_id`, `scholarship_id`, `award_date`) | No duplicate award on the same day |

**Relations:** links one `student` and one `scholarship`.

### 3.10 `payslip` (weak entity)
**Purpose:** monthly salary slip of an employee. Identified by the employee plus the year and month.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `employee_id` | int | PK (part), FK → `employee`, ON DELETE CASCADE | Paid employee |
| `pay_year` | int | PK (part), CHECK 2000–2100 | Year of the slip |
| `pay_month` | int | PK (part), CHECK 1–12 | Month of the slip |
| `gross_salary` | numeric(9,2) | NOT NULL, CHECK > 0 | Gross salary of the month |
| `deductions` | numeric(9,2) | NOT NULL, DEFAULT 0, CHECK ≥ 0 and < `gross_salary` | Taxes and other deductions |
| `paid_date` | date | NULL allowed | Date the salary was transferred (NULL = not paid yet) |

**Relations:** belongs to exactly one `employee`. Net salary is **not stored**: it is `gross_salary - deductions`.

### 3.11 `invoice_status` (ENUM)
**Purpose:** fixed list of invoice statuses.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `code` | int | PK | Status code |
| `label` | varchar(30) | NOT NULL, UNIQUE | 1 Pending, 2 Partially Paid, 3 Paid, 4 Overdue |

### 3.12 `payment_method` (ENUM)
**Purpose:** fixed list of payment methods.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `code` | int | PK | Method code |
| `label` | varchar(30) | NOT NULL, UNIQUE | 1 Cash, 2 Credit Card, 3 Bank Transfer, 4 Check, 5 Direct Debit |

### 3.13 `job_position` (ENUM)
**Purpose:** fixed list of job titles.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `code` | int | PK | Position code |
| `label` | varchar(50) | NOT NULL, UNIQUE | 1 Accountant, 2 Cashier, 3 Payroll Clerk, 4 Lecturer, 5 Administrator, 6 IT Support, 7 Librarian, 8 Secretary |

## 4. Design decisions (to reuse in the README)

- **Inheritance (overlapping):** `person` holds the common data; `student` and `employee` hold role-specific data. A person can be both (for example a student who works as a teaching assistant).
- **Weak entities:** `installment` and `payslip` have no meaning without their parent, hence composite keys and `ON DELETE CASCADE`.
- **Associative entity:** `scholarship_award` has its own `award_id` and a date, so the same scholarship can be granted to the same student again in another year.
- **ENUM tables:** statuses, methods and positions are key/value tables instead of free text, which prevents typing errors and keeps the data consistent.
- **Derived data:** the net salary is not stored (`gross_salary - deductions`) to avoid redundancy.
- **Deliberate redundancy:** `invoice.total_amount` and `invoice.status_code` could be derived from installments and payments. They are kept on purpose so the balance of a student can be displayed quickly without aggregating thousands of rows. The data generator keeps them consistent.
- **Traceability:** `payment.recorded_by` links every payment to the employee who entered it.
