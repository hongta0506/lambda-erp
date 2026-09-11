"""
HR and Payroll Business Actions for lambda_erp plugin.
"""

from lambda_erp.database import get_db
from lambda_erp.utils import _dict, nowdate
from lambda_erp.exceptions import ValidationError
from erp_hr.models import Attendance, SalarySlip


def mark_bulk_attendance(args: dict) -> dict:
    """Action: Bulk mark attendance for a list of employees on a specific date."""
    db = get_db()
    employee_list = args.get("employee_list") or []
    attendance_date = args.get("attendance_date")
    status = args.get("status") or "Present"

    if not employee_list:
        raise ValidationError("employee_list cannot be empty")
    if not attendance_date:
        raise ValidationError("attendance_date is required")

    created = []
    skipped = []
    for emp_id in employee_list:
        existing = db.sql(
            'SELECT name FROM "Attendance" WHERE employee = ? AND attendance_date = ? AND docstatus != 2',
            [emp_id, attendance_date],
        )
        if existing:
            skipped.append(emp_id)
            continue

        emp_row = db.sql('SELECT name, employee_name, company FROM "Employee" WHERE name = ?', [emp_id])
        if not emp_row:
            skipped.append(emp_id)
            continue

        att = Attendance(
            employee=emp_id,
            employee_name=emp_row[0].get("employee_name"),
            company=emp_row[0].get("company"),
            attendance_date=attendance_date,
            status=status,
        )
        att.save()
        att.submit()
        created.append(att.name)

    return {
        "success": True,
        "date": attendance_date,
        "created_count": len(created),
        "created": created,
        "skipped_count": len(skipped),
        "skipped": skipped,
    }


def generate_salary_slip_from_structure(args: dict) -> dict:
    """Action: Generate draft salary slip for employee copied from active Salary Structure."""
    db = get_db()
    employee = args.get("employee")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    posting_date = args.get("posting_date")

    if not employee or not start_date or not end_date:
        raise ValidationError("employee, start_date, and end_date are required")
    str_rows = db.sql(
        'SELECT name FROM "Salary Structure" WHERE employee = ? AND is_active = 1 AND docstatus = 0 ORDER BY creation DESC LIMIT 1',
        [employee],
    )
    if not str_rows:
        raise ValidationError(f"No active Salary Structure found for employee {employee}")

    str_name = str_rows[0]["name"]
    earnings = db.sql(
        'SELECT salary_component, amount FROM "Salary Structure Earning" WHERE parent = ?',
        [str_name],
    )
    deductions = db.sql(
        'SELECT salary_component, amount FROM "Salary Structure Deduction" WHERE parent = ?',
        [str_name],
    )

    slip = SalarySlip(
        employee=employee,
        start_date=start_date,
        end_date=end_date,
        posting_date=posting_date or nowdate(),
        salary_structure=str_name,
        earnings=[{"salary_component": r["salary_component"], "amount": r["amount"]} for r in earnings],
        deductions=[{"salary_component": r["salary_component"], "amount": r["amount"]} for r in deductions],
    )
    slip.save()
    return {
        "success": True,
        "salary_slip": slip.name,
        "gross_pay": slip.gross_pay,
        "net_pay": slip.net_pay,
    }
