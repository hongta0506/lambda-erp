#!/usr/bin/env python3
"""
Comprehensive tests for HRM, Attendance & Payroll plugin (erp_hr).
Verifies:
  1. Plugin registration (tables, masters, doctypes, actions, chat)
  2. Database schema initialization via apply_plugin_schema()
  3. Master records (Department, Designation, Employee)
  4. Attendance tracking & unique daily constraint
  5. Bulk attendance action
  6. Leave Application workflow (draft -> submit approved)
  7. Salary Structure calculation
  8. Salary Slip calculation + GL Entry creation on submit + reversal on cancel
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lambda_erp.database import setup, get_db
from lambda_erp.exceptions import ValidationError
from lambda_erp.accounting.chart_of_accounts import setup_chart_of_accounts
from api.services import (
    _PLUGIN_TABLES,
    MASTER_TABLES,
    DOCUMENT_CLASSES,
    REGISTERED_ACTIONS,
    CHAT_DOCTYPES,
    apply_plugin_schema,
)
import erp_hr


def test_hr_plugin_full_lifecycle():
    # 1. Setup isolated database
    fd, db_path = tempfile.mkstemp(suffix=".db", prefix="test_hr_")
    os.close(fd)
    os.environ["LAMBDA_ERP_DB"] = db_path

    try:
        setup(db_path)
        db = get_db()

        # 2. Register erp_hr plugin
        erp_hr.register()

        # Check registrations
        assert any("Department" in d for d in _PLUGIN_TABLES)
        assert "employee" in MASTER_TABLES
        assert "department" in MASTER_TABLES
        assert "Attendance" in DOCUMENT_CLASSES
        assert "Salary Slip" in DOCUMENT_CLASSES
        assert "mark_bulk_attendance" in REGISTERED_ACTIONS
        assert "attendance" in CHAT_DOCTYPES

        # Apply schema to DB
        apply_plugin_schema()

        # Verify tables created
        cols = db._get_table_columns("Employee")
        assert "employee_name" in cols
        assert "bank_name" in cols

        # 3. Create Company and Chart of Accounts for GL testing
        db.conn.execute(
            'INSERT INTO "Company" (name, company_name, default_currency) VALUES (?, ?, ?)',
            ["Maxell Tech", "Maxell Tech", "VND"],
        )
        db.commit()

        # Create Accounts via setup_chart_of_accounts
        setup_chart_of_accounts("Maxell Tech", "VND")

        # 4. Master: Department & Designation
        db.conn.execute(
            'INSERT INTO "Department" (name, department_name, company) VALUES (?, ?, ?)',
            ["DEP-IT", "Engineering", "Maxell Tech"],
        )
        db.conn.execute(
            'INSERT INTO "Designation" (name, designation_name) VALUES (?, ?)',
            ["Software Engineer", "Software Engineer"],
        )
        db.conn.execute(
            'INSERT INTO "Leave Type" (name, leave_type_name) VALUES (?, ?)',
            ["Annual Leave", "Annual Leave"],
        )
        db.conn.execute(
            'INSERT INTO "Salary Component" (name, type) VALUES (?, ?)',
            ["Basic Salary", "Earning"],
        )
        db.conn.execute(
            'INSERT INTO "Salary Component" (name, type) VALUES (?, ?)',
            ["Meal Allowance", "Earning"],
        )
        db.conn.execute(
            'INSERT INTO "Salary Component" (name, type) VALUES (?, ?)',
            ["Social Insurance", "Deduction"],
        )
        db.commit()

        # Master: Employee
        emp_id = "EMP0001"
        db.conn.execute(
            '''INSERT INTO "Employee" (
                name, first_name, last_name, employee_name, company, department, designation,
                cell_number, personal_email, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            [
                emp_id,
                "Nam",
                "Nguyen",
                "Nam Nguyen",
                "Maxell Tech",
                "DEP-IT",
                "Software Engineer",
                "0987654321",
                "nam@example.com",
                "Active",
            ],
        )
        db.commit()

        # 5. Attendance
        att_cls = DOCUMENT_CLASSES["Attendance"]
        att = att_cls({
            "employee": emp_id,
            "attendance_date": "2026-10-01",
            "status": "Present",
            "working_hours": 8.0,
        })
        att.save()
        att.submit()
        assert att.docstatus == 1

        # Duplicate attendance check on same date should fail
        att_dup = att_cls({
            "employee": emp_id,
            "attendance_date": "2026-10-01",
            "status": "Absent",
        })
        dup_failed = False
        try:
            att_dup.save()
        except ValidationError:
            dup_failed = True
        assert dup_failed, "Duplicate attendance on same date must raise ValidationError"

        # Test bulk attendance action
        from erp_hr.actions import mark_bulk_attendance
        bulk_res = mark_bulk_attendance({
            "employee_list": [emp_id],
            "attendance_date": "2026-10-02",
            "status": "Present",
        })
        assert bulk_res["created_count"] == 1
        assert bulk_res["skipped_count"] == 0

        # 6. Leave Application
        leave_cls = DOCUMENT_CLASSES["Leave Application"]
        leave = leave_cls({
            "employee": emp_id,
            "leave_type": "Annual Leave",
            "from_date": "2026-10-10",
            "to_date": "2026-10-12",
        })
        leave.save()
        assert leave.total_leave_days == 3
        leave.submit()
        assert leave.status == "Approved"
        assert leave.docstatus == 1

        # 7. Salary Structure
        sal_str_cls = DOCUMENT_CLASSES["Salary Structure"]
        sal_str = sal_str_cls({
            "employee": emp_id,
            "company": "Maxell Tech",
            "is_active": 1,
            "earnings": [
                {"salary_component": "Basic Salary", "amount": 20000000},
                {"salary_component": "Meal Allowance", "amount": 1000000},
            ],
            "deductions": [
                {"salary_component": "Social Insurance", "amount": 2100000},
            ],
        })
        sal_str.save()
        assert sal_str.total_earning == 21000000
        assert sal_str.total_deduction == 2100000
        assert sal_str.net_pay == 18900000

        # 8. Salary Slip & GL Posting
        slip_cls = DOCUMENT_CLASSES["Salary Slip"]
        slip = slip_cls({
            "employee": emp_id,
            "company": "Maxell Tech",
            "start_date": "2026-10-01",
            "end_date": "2026-10-31",
            "posting_date": "2026-10-31",
            "earnings": [
                {"salary_component": "Basic Salary", "amount": 20000000},
                {"salary_component": "Meal Allowance", "amount": 1000000},
            ],
            "deductions": [
                {"salary_component": "Social Insurance", "amount": 2100000},
            ],
        })
        slip.save()
        assert slip.gross_pay == 21000000
        assert slip.net_pay == 18900000
        assert slip.expense_account == "Salary Expense - MAXE"
        assert slip.payable_account == "Salary Payable - MAXE"

        # Submit Salary Slip -> check GL entries
        slip.submit()
        assert slip.status == "Submitted"
        assert slip.docstatus == 1

        gl_entries = db.sql(
            'SELECT account, debit, credit FROM "GL Entry" WHERE voucher_no = ? AND voucher_type = ?',
            [slip.name, "Salary Slip"],
        )
        assert len(gl_entries) == 2
        debit_entry = next(e for e in gl_entries if e["debit"] > 0)
        credit_entry = next(e for e in gl_entries if e["credit"] > 0)
        assert debit_entry["account"] == "Salary Expense - MAXE"
        assert debit_entry["debit"] == 21000000
        assert credit_entry["account"] == "Salary Payable - MAXE"
        assert credit_entry["credit"] == 21000000

        # Cancel Salary Slip -> check reverse GL entries
        slip.cancel()
        assert slip.status == "Cancelled"
        assert slip.docstatus == 2

        all_gl = db.sql(
            'SELECT debit, credit FROM "GL Entry" WHERE voucher_no = ? AND voucher_type = ?',
            [slip.name, "Salary Slip"],
        )
        # 2 original entries + 2 reversal entries = 4 entries, net sum = 0
        total_debit = sum(e["debit"] for e in all_gl)
        total_credit = sum(e["credit"] for e in all_gl)
        assert total_debit == total_credit == 42000000

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    test_hr_plugin_full_lifecycle()
    print("All HRM, Attendance & Payroll plugin tests passed successfully!")
