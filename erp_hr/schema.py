"""
Database schemas for HRM, Attendance & Payroll plugin (erp_hr).
Compatible with SQLite and PostgreSQL via db._ddl() translation.
"""

SCHEMA_TABLES = [
    """CREATE TABLE IF NOT EXISTS "Department" (
        name TEXT PRIMARY KEY,
        department_name TEXT,
        parent_department TEXT,
        company TEXT,
        is_group INTEGER DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS "Designation" (
        name TEXT PRIMARY KEY,
        designation_name TEXT,
        description TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS "Employee" (
        name TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        employee_name TEXT,
        gender TEXT,
        date_of_birth TEXT,
        date_of_joining TEXT,
        relieving_date TEXT,
        status TEXT DEFAULT 'Active',
        department TEXT,
        designation TEXT,
        company TEXT,
        user_id TEXT,
        cell_number TEXT,
        personal_email TEXT,
        company_email TEXT,
        bank_name TEXT,
        bank_ac_no TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS "Leave Type" (
        name TEXT PRIMARY KEY,
        leave_type_name TEXT,
        max_days_allowed REAL DEFAULT 0,
        is_lwp INTEGER DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS "Leave Application" (
        name TEXT PRIMARY KEY,
        employee TEXT,
        employee_name TEXT,
        leave_type TEXT,
        from_date TEXT,
        to_date TEXT,
        total_leave_days REAL DEFAULT 0,
        description TEXT,
        status TEXT DEFAULT 'Open',
        company TEXT,
        docstatus INTEGER DEFAULT 0,
        creation TEXT,
        modified TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS "Attendance" (
        name TEXT PRIMARY KEY,
        employee TEXT,
        employee_name TEXT,
        attendance_date TEXT,
        status TEXT DEFAULT 'Present',
        in_time TEXT,
        out_time TEXT,
        working_hours REAL DEFAULT 8.0,
        company TEXT,
        docstatus INTEGER DEFAULT 0,
        creation TEXT,
        modified TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Component" (
        name TEXT PRIMARY KEY,
        salary_component_abbr TEXT,
        type TEXT DEFAULT 'Earning',
        description TEXT,
        default_amount REAL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Structure" (
        name TEXT PRIMARY KEY,
        employee TEXT,
        employee_name TEXT,
        company TEXT,
        is_active INTEGER DEFAULT 1,
        from_date TEXT,
        total_earning REAL DEFAULT 0,
        total_deduction REAL DEFAULT 0,
        net_pay REAL DEFAULT 0,
        docstatus INTEGER DEFAULT 0,
        creation TEXT,
        modified TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Structure Earning" (
        name TEXT PRIMARY KEY,
        parent TEXT,
        parenttype TEXT,
        parentfield TEXT,
        idx INTEGER DEFAULT 0,
        salary_component TEXT,
        amount REAL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Structure Deduction" (
        name TEXT PRIMARY KEY,
        parent TEXT,
        parenttype TEXT,
        parentfield TEXT,
        idx INTEGER DEFAULT 0,
        salary_component TEXT,
        amount REAL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Slip" (
        name TEXT PRIMARY KEY,
        employee TEXT,
        employee_name TEXT,
        company TEXT,
        posting_date TEXT,
        start_date TEXT,
        end_date TEXT,
        salary_structure TEXT,
        payment_days REAL DEFAULT 0,
        absent_days REAL DEFAULT 0,
        leave_without_pay REAL DEFAULT 0,
        gross_pay REAL DEFAULT 0,
        total_deduction REAL DEFAULT 0,
        net_pay REAL DEFAULT 0,
        rounded_total REAL DEFAULT 0,
        expense_account TEXT,
        payable_account TEXT,
        status TEXT DEFAULT 'Draft',
        docstatus INTEGER DEFAULT 0,
        creation TEXT,
        modified TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Slip Earning" (
        name TEXT PRIMARY KEY,
        parent TEXT,
        parenttype TEXT,
        parentfield TEXT,
        idx INTEGER DEFAULT 0,
        salary_component TEXT,
        amount REAL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS "Salary Slip Deduction" (
        name TEXT PRIMARY KEY,
        parent TEXT,
        parenttype TEXT,
        parentfield TEXT,
        idx INTEGER DEFAULT 0,
        salary_component TEXT,
        amount REAL DEFAULT 0
    )"""
]
