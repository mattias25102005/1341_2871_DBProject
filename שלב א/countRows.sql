-- countRows.sql : number of rows in each table (for checking + README screenshot)
SELECT 'invoice_status' AS table_name, count(*) AS row_count FROM invoice_status
UNION ALL SELECT 'payment_method', count(*) FROM payment_method
UNION ALL SELECT 'job_position', count(*) FROM job_position
UNION ALL SELECT 'person', count(*) FROM person
UNION ALL SELECT 'program', count(*) FROM program
UNION ALL SELECT 'student', count(*) FROM student
UNION ALL SELECT 'employee', count(*) FROM employee
UNION ALL SELECT 'invoice', count(*) FROM invoice
UNION ALL SELECT 'installment', count(*) FROM installment
UNION ALL SELECT 'payment', count(*) FROM payment
UNION ALL SELECT 'scholarship', count(*) FROM scholarship
UNION ALL SELECT 'scholarship_award', count(*) FROM scholarship_award
UNION ALL SELECT 'payslip', count(*) FROM payslip;
