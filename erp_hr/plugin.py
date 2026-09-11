"""
Plugin registration entrypoint for erp_hr module.
Zero modification to lambda_erp core.
"""

from api.services import (
    register_table,
    register_master,
    register_doctype,
    register_action,
    register_chat_doctype,
)
from erp_hr.schema import SCHEMA_TABLES
from erp_hr.models import (
    LeaveApplication,
    Attendance,
    SalaryStructure,
    SalarySlip,
)
from erp_hr.actions import (
    mark_bulk_attendance,
    generate_salary_slip_from_structure,
)


def register():
    """Register tables, masters, doctypes, actions, and chat bindings for HR."""
    # 1. Register database tables
    for ddl in SCHEMA_TABLES:
        register_table(ddl)

    # 2. Register master entities (exposed via /api/masters/{slug})
    register_master(
        slug="department",
        table="Department",
        name_field="name",
        description="Company departments and organizational hierarchy",
        fields=["name", "department_name", "parent_department", "company", "is_group"],
    )
    register_master(
        slug="designation",
        table="Designation",
        name_field="designation_name",
        description="Employee job titles and designations",
        fields=["name", "designation_name", "description"],
    )
    register_master(
        slug="employee",
        table="Employee",
        name_field="name",
        name_prefix="EMP",
        name_digits=4,
        description="Employee directory and employment details",
        fields=[
            "name",
            "first_name",
            "last_name",
            "employee_name",
            "gender",
            "date_of_birth",
            "date_of_joining",
            "relieving_date",
            "status",
            "department",
            "designation",
            "company",
            "user_id",
            "cell_number",
            "personal_email",
            "company_email",
            "bank_name",
            "bank_ac_no",
        ],
    )
    register_master(
        slug="leave-type",
        table="Leave Type",
        name_field="name",
        description="Leave types such as Annual Leave, Sick Leave, Unpaid Leave",
        fields=["name", "leave_type_name", "max_days_allowed", "is_lwp"],
    )
    register_master(
        slug="salary-component",
        table="Salary Component",
        name_field="name",
        description="Salary components (Basic, Allowance, Social Insurance, Tax)",
        fields=["name", "salary_component_abbr", "type", "description", "default_amount"],
    )

    # 3. Register transaction doctypes (Document classes)
    register_doctype("Leave Application", LeaveApplication, slug="leave-application")
    register_doctype("Attendance", Attendance, slug="attendance")
    register_doctype("Salary Structure", SalaryStructure, slug="salary-structure")
    register_doctype("Salary Slip", SalarySlip, slug="salary-slip")

    # 4. Register chat bindings for AI assistant
    register_chat_doctype("employee", description="Employee profile and personal details")
    register_chat_doctype("attendance", description="Employee daily attendance records")
    register_chat_doctype("leave-application", description="Leave requests and status")
    register_chat_doctype("salary-slip", description="Payroll slips and payments")

    # 5. Register custom business actions
    register_action(
        name="mark_bulk_attendance",
        handler=mark_bulk_attendance,
        description="Bulk mark attendance for multiple employees on a given date",
        parameters={
            "type": "object",
            "properties": {
                "employee_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Employee IDs (e.g. ['EMP0001', 'EMP0002'])",
                },
                "attendance_date": {"type": "string", "description": "Date YYYY-MM-DD"},
                "status": {"type": "string", "enum": ["Present", "Absent", "On Leave", "Half Day"]},
            },
            "required": ["employee_list", "attendance_date"],
        },
        minimum_role="manager",
    )
    register_action(
        name="generate_salary_slip_from_structure",
        handler=generate_salary_slip_from_structure,
        description="Generate draft salary slip for an employee from active Salary Structure",
        parameters={
            "type": "object",
            "properties": {
                "employee": {"type": "string", "description": "Employee ID"},
                "start_date": {"type": "string", "description": "Payroll period start date"},
                "end_date": {"type": "string", "description": "Payroll period end date"},
                "posting_date": {"type": "string", "description": "Posting date (optional)"},
            },
            "required": ["employee", "start_date", "end_date"],
        },
        minimum_role="manager",
    )
