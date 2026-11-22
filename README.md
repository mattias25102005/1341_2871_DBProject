# Stage A – College Accounting Database

| | |
|---|---|
| **Authors** | **[TO FILL: name 1 – ID last 4 digits]**, **[TO FILL: name 2 – ID last 4 digits]** |
| **System** | College (מכללה) |
| **Unit** | Accounting department (אגף חשבונות) |
| **DBMS** | PostgreSQL (Docker) + pgAdmin |

## Table of contents
1. [Introduction](#1-introduction)
2. [Screens (prototype)](#2-screens-prototype)
3. [ERD and DSD](#3-erd-and-dsd)
4. [Data dictionary](#4-data-dictionary)
5. [Creating the database](#5-creating-the-database)
6. [Data insertion (3 methods)](#6-data-insertion-3-methods)
7. [Backup and restore](#7-backup-and-restore)
8. [Repository structure](#8-repository-structure)

## 1. Introduction
The accounting department of a college handles two money flows.

- **Incoming money:** students are billed with **invoices**, each split into **installments**. Students pay through **payments**, which are entered by an accounting employee. Students can also receive **scholarships**.
- **Outgoing money:** every employee receives a monthly **payslip**.

The database stores people (students and employees), study programs, invoices, installments, payments, scholarships and their awards, and payslips.

Main functionality of the system:
1. Follow a student account: invoices, installments, payments and balance.
2. Enter a payment and link it to the employee who recorded it.
3. Manage scholarships and award them to students.
4. Manage payroll: monthly payslips and a monthly report.

## 2. Screens (prototype)
The 4 screens were generated with Google AI Studio (mock data, no database).

**AI Studio link:** **[TO FILL: paste the link]**

| Screen | Image |
|---|---|
| 1. Student account | ![screen 1](שלב%20א/screenshots/screen1_student_account.png) |
| 2. Payment entry | ![screen 2](שלב%20א/screenshots/screen2_payment_entry.png) |
| 3. Scholarships | ![screen 3](שלב%20א/screenshots/screen3_scholarships.png) |
| 4. Payroll | ![screen 4](שלב%20א/screenshots/screen4_payroll.png) |

## 3. ERD and DSD

### ERD
![ERD](שלב%20א/screenshots/erd.png)

### DSD
![DSD](שלב%20א/screenshots/dsd.png)

### Design decisions
- **Inheritance (overlapping):** `person` holds the common data. `student` and `employee` hold role-specific data. A person can be both, for example a student who works as an assistant.
- **Weak entities:** `installment` (of `invoice`) and `payslip` (of `employee`) have no meaning without their parent, so they use composite keys and `ON DELETE CASCADE`.
- **Associative entity:** `scholarship_award` has its own key and a date, so the same scholarship can be granted to the same student again in another year.
- **ENUM tables:** `invoice_status`, `payment_method` and `job_position` are key/value tables, which prevents typing errors.
- **No derived salary:** the net salary is not stored. It equals `gross_salary - deductions` and is computed in queries.
- **Deliberate redundancy:** `invoice.total_amount` and `invoice.status_code` could be derived from installments and payments. They are kept so a student's balance can be shown quickly without aggregating many rows. The generated data keeps them consistent.
- **Traceability:** `payment.recorded_by` links each payment to the employee who entered it.
- **Normalization:** every non-key attribute depends on the key, the whole key and nothing but the key, so the schema is in 3NF.

**[TO FILL, only if true: the automatic ERD → DSD conversion did not generate the foreign keys, so the DSD was completed by hand to match `createTables.sql`.]**

## 4. Data dictionary
The full dictionary (purpose, fields and relations of each table) is in [`שלב א/data_dictionary.md`](שלב%20א/data_dictionary.md).

## 5. Creating the database
The database runs in Docker (PostgreSQL + pgAdmin). The file `createTables.sql` is executed automatically at the first start of the container.

- `createTables.sql` creates the 13 tables (10 entities + 3 ENUM tables) with primary keys, foreign keys, `NOT NULL`, `UNIQUE`, `CHECK` and `DEFAULT` constraints.
- `dropTables.sql` deletes the tables in reverse dependency order (children first).

![tables in pgAdmin](שלב%20א/screenshots/pgadmin_tables.png)

## 6. Data insertion (3 methods)

| # | Method | Tables | Files |
|---|--------|--------|-------|
| 1 | Hand-written `INSERT` statements | `invoice_status`, `payment_method`, `job_position` | `insertTables.sql` |
| 2 | Python script (Faker) generating `INSERT` statements | `person`, `employee`, `student`, `invoice`, `installment`, `payment`, `scholarship_award`, `payslip` | `Programing/` |
| 3 | Import of CSV files with `\copy` | `program`, `scholarship` | `DataImportFiles/` |

Row counts obtained:

| Table | Rows | Table | Rows |
|---|---|---|---|
| `invoice_status` | 4 | `invoice` | 20 000 |
| `payment_method` | 5 | `installment` | 59 973 |
| `job_position` | 8 | `payment` | 28 004 |
| `person` | 10 560 | `scholarship` | 500 |
| `student` | 10 000 | `scholarship_award` | 3 000 |
| `employee` | 600 | `payslip` | 13 200 |
| `program` | 500 | | |

Three tables exceed 20 000 rows. Every non-ENUM table has at least 500 rows. The ENUM tables are exempt.

### Method 1 – manual INSERT
![method 1](שלב%20א/screenshots/insert_method1.png)

### Method 2 – Python script
The script reads the program prices, then generates people, invoices, installments (which add up to the invoice total), payments and payslips. Invoice statuses are computed from the payments, and dates are kept consistent (no payment before its invoice, no student under 18, and so on).

![method 2](שלב%20א/screenshots/insert_method2.png)

### Method 3 – CSV import
![method 3](שלב%20א/screenshots/insert_method3.png)

### Result: row counts
![row counts](שלב%20א/screenshots/count_rows.png)

## 7. Backup and restore
Two different methods were used.

| # | Method | File |
|---|--------|------|
| 1 | Command line: `pg_dump` | `backup_2026-11-22.sql` |
| 2 | pgAdmin user interface (Backup) | `backup_2026-11-22_pgadmin.backup` |

### Backup – command line
![backup cli](שלב%20א/screenshots/backup_cli.png)

### Backup – pgAdmin
![backup pgadmin](שלב%20א/screenshots/backup_pgadmin.png)

### Restore test on the same computer
The backup was first restored into a new, empty database (`restore_test`) and the row counts were compared with the original database. All 13 tables and all rows were recovered.

![local restore](שלב%20א/screenshots/restore_local_test.png)

### Restore on another computer
The file `backup_2026-11-22.sql` was restored on another computer, into a fresh PostgreSQL container, with the script `restore_backup.bat`.

**[TO FILL: whose computer, and the date]**

![restore](שלב%20א/screenshots/restore.png)

## 8. Repository structure
```
XXXX_YYYY_DBProject/
├── README.md
└── שלב א/
    ├── specification.md
    ├── data_dictionary.md
    ├── ERD, DSD (files)
    ├── createTables.sql
    ├── dropTables.sql
    ├── insertTables.sql
    ├── selectAll.sql
    ├── countRows.sql
    ├── screenshots/
    ├── Programing/          (generate_data.py and its output)
    ├── DataImportFiles/     (CSV files and make_csv.py)
    ├── backup_2026-11-22.sql
    ├── backup_2026-11-22_pgadmin.backup
    └── restore_backup.bat
```
