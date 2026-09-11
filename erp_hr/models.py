"""
HR, Attendance and Payroll Document Models for lambda_erp plugin.
Zero modification to lambda_erp core.
"""

from datetime import datetime
from lambda_erp.model import Document
from lambda_erp.utils import _dict, flt, nowdate
from lambda_erp.database import get_db
from lambda_erp.accounting.general_ledger import make_gl_entries, make_reverse_gl_entries
from lambda_erp.exceptions import ValidationError


def _find_account(company: str, name_prefix: str, fallback_type: str) -> str:
    """Helper to locate standard accounts in Company chart of accounts."""
    db = get_db()
    if not db or not company:
        return ""
    rows = db.sql(
        'SELECT name FROM "Account" WHERE company = ? AND name LIKE ? AND disabled = 0 LIMIT 1',
        [company, f"{name_prefix}%"],
    )
    if rows:
        return rows[0]["name"]
    rows = db.sql(
        'SELECT name FROM "Account" WHERE company = ? AND account_type = ? AND disabled = 0 LIMIT 1',
        [company, fallback_type],
    )
    if rows:
        return rows[0]["name"]
    return ""


class LeaveApplication(Document):
    DOCTYPE = "Leave Application"
    PREFIX = "LV"
    LINK_FIELDS = {
        "employee": "Employee",
        "company": "Company",
        "leave_type": "Leave Type",
    }

    def validate(self):
        if not self.get("employee"):
            raise ValidationError("Employee is required for Leave Application")
        if not self.get("leave_type"):
            raise ValidationError("Leave Type is required for Leave Application")
        if not self.get("from_date") or not self.get("to_date"):
            raise ValidationError("From Date and To Date are required")

        if not self.get("total_leave_days"):
            d1 = datetime.strptime(str(self.from_date), "%Y-%m-%d")
            d2 = datetime.strptime(str(self.to_date), "%Y-%m-%d")
            delta = (d2 - d1).days + 1
            if delta <= 0:
                raise ValidationError("To Date cannot be earlier than From Date")
            self._data["total_leave_days"] = delta

        db = get_db()
        if not self.get("company"):
            emp_co = db.get_value("Employee", self.employee, "company")
            self._data["company"] = emp_co or ""
        if not self.get("employee_name"):
            emp_name = db.get_value("Employee", self.employee, "employee_name")
            self._data["employee_name"] = emp_name or ""

    def on_submit(self):
        self._data["status"] = "Approved"

    def on_cancel(self):
        self._data["status"] = "Cancelled"


class Attendance(Document):
    DOCTYPE = "Attendance"
    PREFIX = "ATT"
    LINK_FIELDS = {
        "employee": "Employee",
        "company": "Company",
    }

    def validate(self):
        if not self.get("employee"):
            raise ValidationError("Employee is required for Attendance")
        if not self.get("attendance_date"):
            raise ValidationError("Attendance Date is required")

        valid_statuses = {"Present", "Absent", "On Leave", "Half Day"}
        status = self.get("status") or "Present"
        if status not in valid_statuses:
            raise ValidationError(f"Invalid attendance status '{status}'. Must be one of {valid_statuses}")
        self._data["status"] = status

        db = get_db()
        if not self.get("company"):
            self._data["company"] = db.get_value("Employee", self.employee, "company") or ""
        if not self.get("employee_name"):
            self._data["employee_name"] = db.get_value("Employee", self.employee, "employee_name") or ""

        # Check duplicate record for same day
        existing = db.sql(
            'SELECT name FROM "Attendance" WHERE employee = ? AND attendance_date = ? AND name != ? AND docstatus != 2',
            [self.employee, self.attendance_date, self.name or ""],
        )
        if existing:
            raise ValidationError(f"Attendance record already exists for {self.employee} on {self.attendance_date}")


class SalaryStructure(Document):
    DOCTYPE = "Salary Structure"
    PREFIX = "SAL-STR"
    CHILD_TABLES = {
        "earnings": ("Salary Structure Earning", None),
        "deductions": ("Salary Structure Deduction", None),
    }
    LINK_FIELDS = {
        "employee": "Employee",
        "company": "Company",
    }

    def validate(self):
        if not self.get("employee"):
            raise ValidationError("Employee is required for Salary Structure")

        db = get_db()
        if not self.get("company"):
            self._data["company"] = db.get_value("Employee", self.employee, "company") or ""
        if not self.get("employee_name"):
            self._data["employee_name"] = db.get_value("Employee", self.employee, "employee_name") or ""

        tot_earn = sum(flt(r.get("amount", 0)) for r in self.get("earnings") or [])
        tot_ded = sum(flt(r.get("amount", 0)) for r in self.get("deductions") or [])
        self._data["total_earning"] = flt(tot_earn, 2)
        self._data["total_deduction"] = flt(tot_ded, 2)
        self._data["net_pay"] = flt(tot_earn - tot_ded, 2)


class SalarySlip(Document):
    DOCTYPE = "Salary Slip"
    PREFIX = "SAL"
    CHILD_TABLES = {
        "earnings": ("Salary Slip Earning", None),
        "deductions": ("Salary Slip Deduction", None),
    }
    LINK_FIELDS = {
        "employee": "Employee",
        "company": "Company",
        "expense_account": "Account",
        "payable_account": "Account",
    }

    def validate(self):
        if not self.get("employee"):
            raise ValidationError("Employee is required for Salary Slip")
        if not self.get("posting_date"):
            self._data["posting_date"] = nowdate()

        db = get_db()
        if not self.get("company"):
            self._data["company"] = db.get_value("Employee", self.employee, "company") or ""
        if not self.get("employee_name"):
            self._data["employee_name"] = db.get_value("Employee", self.employee, "employee_name") or ""

        # Ensure GL accounts
        if not self.get("expense_account") and self.company:
            self._data["expense_account"] = _find_account(self.company, "Salary Expense", "Expense")
        if not self.get("payable_account") and self.company:
            self._data["payable_account"] = _find_account(self.company, "Salary Payable", "Payable")

        gross = sum(flt(r.get("amount", 0)) for r in self.get("earnings") or [])
        deductions = sum(flt(r.get("amount", 0)) for r in self.get("deductions") or [])
        net = gross - deductions

        self._data["gross_pay"] = flt(gross, 2)
        self._data["total_deduction"] = flt(deductions, 2)
        self._data["net_pay"] = flt(net, 2)
        self._data["rounded_total"] = flt(round(net, 2), 2)

    def on_submit(self):
        self._data["status"] = "Submitted"
        if not self.company or not self.expense_account or not self.payable_account:
            return  # Standalone mode without financial accounts

        gross = flt(self.gross_pay)
        net = flt(self.net_pay)
        ded = flt(self.total_deduction)

        if gross <= 0:
            return

        gl_map = [
            _dict(
                posting_date=self.posting_date,
                account=self.expense_account,
                debit=gross,
                credit=0,
                against=self.payable_account,
                voucher_type=self.DOCTYPE,
                voucher_no=self.name,
                company=self.company,
                remarks=f"Salary Slip for {self.employee} ({self.posting_date})",
            ),
            _dict(
                posting_date=self.posting_date,
                account=self.payable_account,
                debit=0,
                credit=gross,
                against=self.expense_account,
                voucher_type=self.DOCTYPE,
                voucher_no=self.name,
                company=self.company,
                remarks=f"Salary Slip for {self.employee} ({self.posting_date})",
            ),
        ]
        make_gl_entries(gl_map)

    def on_cancel(self):
        self._data["status"] = "Cancelled"
        make_reverse_gl_entries(voucher_type=self.DOCTYPE, voucher_no=self.name)
