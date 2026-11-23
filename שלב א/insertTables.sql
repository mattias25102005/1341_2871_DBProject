-- =====================================================================
-- insertTables.sql  -  Stage A
-- METHOD 1: hand-written INSERT statements (small ENUM / lookup tables)
--
-- The other two methods fill the remaining tables:
--   METHOD 2: Python script  -> Programing/output/insert_generated.sql
--             (person, employee, student, invoice, installment,
--              payment, scholarship_award, payslip)
--   METHOD 3: CSV import     -> DataImportFiles/program.csv
--                               DataImportFiles/scholarship.csv
-- Load order: this file, then the 2 CSV files, then the Python output.
-- =====================================================================

INSERT INTO invoice_status (code, label) VALUES
  (1, 'Pending'),
  (2, 'Partially Paid'),
  (3, 'Paid'),
  (4, 'Overdue');

INSERT INTO payment_method (code, label) VALUES
  (1, 'Cash'),
  (2, 'Credit Card'),
  (3, 'Bank Transfer'),
  (4, 'Check'),
  (5, 'Direct Debit');

INSERT INTO job_position (code, label) VALUES
  (1, 'Accountant'),
  (2, 'Cashier'),
  (3, 'Payroll Clerk'),
  (4, 'Lecturer'),
  (5, 'Administrator'),
  (6, 'IT Support'),
  (7, 'Librarian'),
  (8, 'Secretary');
