# System Specification – College Accounting Department

**System:** College (מכללה)
**Unit:** Accounting department (אגף חשבונות)

## 1. Purpose
The system manages the money flows of a college: the tuition that students owe and pay, the scholarships they receive, and the salaries paid to the staff.

## 2. Stored data
| Group | Data |
|---|---|
| People | Common identity data (national ID, name, birth date, email, phone). A person can be a **student**, an **employee**, or both. |
| Students | Study program, enrollment date, active or not. |
| Employees | Job position, hire date, base salary. |
| Programs | Name, annual price, duration in years. |
| Billing | Invoices (issue date, due date, total, status), their installments (schedule), and the payments received (date, amount, method, employee who recorded it). |
| Scholarships | Scholarship catalogue (name, amount, criteria) and the awards given to students with their date. |
| Payroll | Monthly payslip of each employee (gross salary, deductions, payment date). |
| Lookup tables | Invoice status, payment method, job position. |

## 3. Main functionality
1. **Student account:** show a student's invoices, installments, payments and remaining balance.
2. **Payment entry:** record a payment for an invoice with its method, and keep track of the employee who entered it.
3. **Scholarships:** create scholarships and award them to students.
4. **Payroll:** list the payslips of each employee and produce a monthly payroll report.

## 4. Screens of the prototype
| # | Screen | Main content |
|---|---|---|
| 1 | Student account | Student details, invoices, installments, payments, balance |
| 2 | Payment entry | Form: invoice, amount, date, method, recording employee |
| 3 | Scholarships | Scholarship list, award form, awards per student |
| 4 | Payroll | Payslips per employee and monthly report |

The screens were generated with Google AI Studio using mock data, without a database connection.

## 5. Main business rules
- Every person is born before 2010-01-01.
- An invoice due date is never earlier than its issue date.
- The installments of an invoice add up to the invoice total.
- An invoice is *Paid*, *Partially Paid*, *Pending* or *Overdue*, depending on the payments received and its due date.
- Every payment is recorded by an employee.
- A payslip's deductions are lower than its gross salary. The net salary is computed, not stored.
- The same scholarship can be awarded to the same student on different dates.
