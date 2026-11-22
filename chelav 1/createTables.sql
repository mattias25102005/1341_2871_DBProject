-- ===== ENUM tables (key / value) =====
CREATE TABLE invoice_status (
  code   int PRIMARY KEY,
  label  varchar(30) NOT NULL UNIQUE
);

CREATE TABLE payment_method (
  code   int PRIMARY KEY,
  label  varchar(30) NOT NULL UNIQUE
);

CREATE TABLE job_position (
  code   int PRIMARY KEY,
  label  varchar(50) NOT NULL UNIQUE
);

-- ===== Inheritance: person -> student / employee =====
CREATE TABLE person (
  person_id   int PRIMARY KEY,
  national_id varchar(9)   NOT NULL UNIQUE,
  first_name  varchar(50)  NOT NULL,
  last_name   varchar(50)  NOT NULL,
  birth_date  date         NOT NULL CHECK (birth_date < DATE '2010-01-01'),
  email       varchar(100) NOT NULL UNIQUE,
  phone       varchar(15)
);

CREATE TABLE program (
  program_id     int PRIMARY KEY,
  name           varchar(80)  NOT NULL UNIQUE,
  annual_price   numeric(8,2) NOT NULL CHECK (annual_price > 0),
  duration_years int          NOT NULL CHECK (duration_years BETWEEN 1 AND 6)
);

CREATE TABLE student (
  person_id       int PRIMARY KEY REFERENCES person(person_id),
  program_id      int     NOT NULL REFERENCES program(program_id),
  enrollment_date date    NOT NULL DEFAULT CURRENT_DATE,
  is_active       boolean NOT NULL DEFAULT TRUE
);

CREATE TABLE employee (
  person_id     int PRIMARY KEY REFERENCES person(person_id),
  position_code int  NOT NULL REFERENCES job_position(code),
  hire_date     date NOT NULL,
  base_salary   numeric(9,2) NOT NULL CHECK (base_salary > 0)
);

-- ===== Billing =====
CREATE TABLE invoice (
  invoice_id   int PRIMARY KEY,
  student_id   int  NOT NULL REFERENCES student(person_id),
  status_code  int  NOT NULL DEFAULT 1 REFERENCES invoice_status(code),
  issue_date   date NOT NULL DEFAULT CURRENT_DATE,
  due_date     date NOT NULL,
  total_amount numeric(9,2) NOT NULL CHECK (total_amount > 0),
  CHECK (due_date >= issue_date)
);

-- Weak entity of invoice
CREATE TABLE installment (
  invoice_id         int NOT NULL REFERENCES invoice(invoice_id) ON DELETE CASCADE,
  installment_number int NOT NULL CHECK (installment_number > 0),
  deadline_date      date NOT NULL,
  amount             numeric(9,2) NOT NULL CHECK (amount > 0),
  PRIMARY KEY (invoice_id, installment_number)
);

-- Payment recorded by an employee
CREATE TABLE payment (
  payment_id   int PRIMARY KEY,
  invoice_id   int  NOT NULL REFERENCES invoice(invoice_id),
  method_code  int  NOT NULL REFERENCES payment_method(code),
  recorded_by  int  NOT NULL REFERENCES employee(person_id),
  payment_date date NOT NULL DEFAULT CURRENT_DATE,
  amount       numeric(9,2) NOT NULL CHECK (amount > 0)
);

-- ===== Scholarships =====
CREATE TABLE scholarship (
  scholarship_id int PRIMARY KEY,
  name           varchar(80)  NOT NULL UNIQUE,
  amount         numeric(8,2) NOT NULL CHECK (amount > 0),
  criteria       varchar(200)
);

-- Associative entity student <-> scholarship
CREATE TABLE scholarship_award (
  award_id       int PRIMARY KEY,
  student_id     int  NOT NULL REFERENCES student(person_id),
  scholarship_id int  NOT NULL REFERENCES scholarship(scholarship_id),
  award_date     date NOT NULL DEFAULT CURRENT_DATE,
  UNIQUE (student_id, scholarship_id, award_date)
);

-- ===== Payroll: weak entity of employee =====
CREATE TABLE payslip (
  employee_id  int NOT NULL REFERENCES employee(person_id) ON DELETE CASCADE,
  pay_year     int NOT NULL CHECK (pay_year BETWEEN 2000 AND 2100),
  pay_month    int NOT NULL CHECK (pay_month BETWEEN 1 AND 12),
  gross_salary numeric(9,2) NOT NULL CHECK (gross_salary > 0),
  deductions   numeric(9,2) NOT NULL DEFAULT 0 CHECK (deductions >= 0),
  paid_date    date,
  PRIMARY KEY (employee_id, pay_year, pay_month),
  CHECK (deductions < gross_salary)
);