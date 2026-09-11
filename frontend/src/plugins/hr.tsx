import { Users } from "lucide-react";
import { registerNavGroup } from "@/lib/nav";
import { registerMaster } from "@/lib/masters";
import { registerDoctype } from "@/lib/doctypes";

// 1. Register Masters (Department, Designation, Leave Type, Salary Component, Employee)
registerMaster({
  slug: "department",
  label: "Department",
  fields: [
    { name: "name", label: "ID", type: "text", required: true },
    { name: "department_name", label: "Department Name", type: "text", required: true },
    { name: "parent_department", label: "Parent Department", type: "link", linkDoctype: "department" },
    { name: "company", label: "Company", type: "link", linkDoctype: "company" },
  ],
  listColumns: ["name", "department_name", "parent_department", "company"],
});

registerMaster({
  slug: "designation",
  label: "Designation",
  fields: [
    { name: "name", label: "ID", type: "text", required: true },
    { name: "designation_name", label: "Designation Name", type: "text", required: true },
    { name: "description", label: "Description", type: "textarea" },
  ],
  listColumns: ["name", "designation_name"],
});

registerMaster({
  slug: "leave-type",
  label: "Leave Type",
  fields: [
    { name: "name", label: "Leave Type", type: "text", required: true },
    { name: "leave_type_name", label: "Leave Type Name", type: "text", required: true },
    { name: "max_days_allowed", label: "Max Days Allowed", type: "number" },
  ],
  listColumns: ["name", "leave_type_name", "max_days_allowed"],
});

registerMaster({
  slug: "salary-component",
  label: "Salary Component",
  fields: [
    { name: "name", label: "Name", type: "text", required: true },
    { name: "salary_component_abbr", label: "Abbreviation", type: "text" },
    { name: "type", label: "Type", type: "select", options: ["Earning", "Deduction"], required: true },
    { name: "description", label: "Description", type: "textarea" },
    { name: "default_amount", label: "Default Amount", type: "currency" },
  ],
  listColumns: ["name", "salary_component_abbr", "type", "default_amount"],
  listFilters: [{ field: "type", label: "Type" }],
});

registerMaster({
  slug: "employee",
  label: "Employee",
  fields: [
    { name: "first_name", label: "First Name", type: "text", required: true },
    { name: "last_name", label: "Last Name", type: "text" },
    { name: "employee_name", label: "Full Name", type: "text", required: true },
    { name: "gender", label: "Gender", type: "select", options: ["Male", "Female", "Other"] },
    { name: "date_of_birth", label: "Date of Birth", type: "date" },
    { name: "date_of_joining", label: "Date of Joining", type: "date" },
    { name: "relieving_date", label: "Relieving Date", type: "date" },
    { name: "status", label: "Status", type: "select", options: ["Active", "Left", "Suspended"], default: "Active" },
    { name: "department", label: "Department", type: "link", linkDoctype: "department" },
    { name: "designation", label: "Designation", type: "link", linkDoctype: "designation" },
    { name: "company", label: "Company", type: "link", linkDoctype: "company" },
    { name: "cell_number", label: "Phone", type: "text" },
    { name: "personal_email", label: "Personal Email", type: "text" },
    { name: "company_email", label: "Company Email", type: "text" },
    { name: "bank_name", label: "Bank Name", type: "text" },
    { name: "bank_ac_no", label: "Bank Account No", type: "text" },
  ],
  listColumns: ["name", "employee_name", "department", "designation", "status", "cell_number"],
  listFilters: [{ field: "status", label: "Status" }],
});

// 2. Register Transaction DocTypes
registerDoctype({
  slug: "attendance",
  label: "Attendance",
  dateField: "attendance_date",
  canSubmit: true,
  canCancel: true,
  conversions: [],
  fields: [
    { name: "employee", label: "Employee", type: "link", linkDoctype: "employee", required: true },
    { name: "employee_name", label: "Employee Name", type: "text", readOnly: true },
    { name: "company", label: "Company", type: "link", linkDoctype: "company" },
    { name: "attendance_date", label: "Attendance Date", type: "date", required: true },
    { name: "status", label: "Status", type: "select", options: ["Present", "Absent", "On Leave", "Half Day"], required: true, default: "Present" },
    { name: "working_hours", label: "Working Hours", type: "number", default: 8.0 },
    { name: "leave_type", label: "Leave Type", type: "link", linkDoctype: "leave-type" },
    { name: "remarks", label: "Remarks", type: "textarea" },
  ],
  childTables: [],
  listColumns: ["name", "employee", "employee_name", "attendance_date", "status", "working_hours", "docstatus"],
  listFilters: ["status"],
});

registerDoctype({
  slug: "leave-application",
  label: "Leave Application",
  dateField: "from_date",
  canSubmit: true,
  canCancel: true,
  conversions: [],
  fields: [
    { name: "employee", label: "Employee", type: "link", linkDoctype: "employee", required: true },
    { name: "leave_type", label: "Leave Type", type: "link", linkDoctype: "leave-type", required: true },
    { name: "from_date", label: "From Date", type: "date", required: true },
    { name: "to_date", label: "To Date", type: "date", required: true },
    { name: "total_leave_days", label: "Total Leave Days", type: "number", readOnly: true },
    { name: "reason", label: "Reason", type: "textarea" },
    { name: "status", label: "Status", type: "select", options: ["Open", "Approved", "Rejected", "Cancelled"], default: "Open" },
  ],
  childTables: [],
  listColumns: ["name", "employee", "leave_type", "from_date", "to_date", "total_leave_days", "status", "docstatus"],
  listFilters: ["status"],
});

registerDoctype({
  slug: "salary-structure",
  label: "Salary Structure",
  dateField: "from_date",
  canSubmit: false,
  canCancel: false,
  conversions: [],
  amountField: "net_pay",
  fields: [
    { name: "employee", label: "Employee", type: "link", linkDoctype: "employee", required: true },
    { name: "company", label: "Company", type: "link", linkDoctype: "company", required: true },
    { name: "from_date", label: "From Date", type: "date" },
    { name: "is_active", label: "Is Active", type: "number", default: 1 },
    { name: "total_earning", label: "Total Earning", type: "currency", readOnly: true },
    { name: "total_deduction", label: "Total Deduction", type: "currency", readOnly: true },
    { name: "net_pay", label: "Net Pay", type: "currency", readOnly: true },
  ],
  childTables: [
    {
      key: "earnings",
      label: "Earnings",
      fields: [
        { name: "salary_component", label: "Salary Component", type: "link", linkDoctype: "salary-component", required: true },
        { name: "amount", label: "Amount", type: "currency", required: true },
      ],
    },
    {
      key: "deductions",
      label: "Deductions",
      fields: [
        { name: "salary_component", label: "Salary Component", type: "link", linkDoctype: "salary-component", required: true },
        { name: "amount", label: "Amount", type: "currency", required: true },
      ],
    },
  ],
  listColumns: ["name", "employee", "company", "is_active", "total_earning", "total_deduction", "net_pay"],
});

registerDoctype({
  slug: "salary-slip",
  label: "Salary Slip",
  dateField: "posting_date",
  amountField: "net_pay",
  canSubmit: true,
  canCancel: true,
  conversions: [],
  fields: [
    { name: "employee", label: "Employee", type: "link", linkDoctype: "employee", required: true },
    { name: "company", label: "Company", type: "link", linkDoctype: "company", required: true },
    { name: "posting_date", label: "Posting Date", type: "date", required: true },
    { name: "start_date", label: "Start Date", type: "date", required: true },
    { name: "end_date", label: "End Date", type: "date", required: true },
    { name: "gross_pay", label: "Gross Pay", type: "currency", readOnly: true },
    { name: "total_deduction", label: "Total Deduction", type: "currency", readOnly: true },
    { name: "net_pay", label: "Net Pay", type: "currency", readOnly: true },
    { name: "status", label: "Status", type: "select", options: ["Draft", "Submitted", "Cancelled"], default: "Draft" },
  ],
  childTables: [
    {
      key: "earnings",
      label: "Earnings",
      fields: [
        { name: "salary_component", label: "Salary Component", type: "link", linkDoctype: "salary-component", required: true },
        { name: "amount", label: "Amount", type: "currency", required: true },
      ],
    },
    {
      key: "deductions",
      label: "Deductions",
      fields: [
        { name: "salary_component", label: "Salary Component", type: "link", linkDoctype: "salary-component", required: true },
        { name: "amount", label: "Amount", type: "currency", required: true },
      ],
    },
  ],
  listColumns: ["name", "employee", "start_date", "end_date", "gross_pay", "net_pay", "status", "docstatus"],
  listFilters: ["status"],
});

// 3. Register Navigation Group
registerNavGroup(
  {
    label: "HR & Payroll",
    icon: <Users className="h-4 w-4" />,
    items: [
      { label: "Employee", path: "/masters/employee" },
      { label: "Attendance", path: "/app/attendance" },
      { label: "Leave Application", path: "/app/leave-application" },
      { label: "Salary Structure", path: "/app/salary-structure" },
      { label: "Salary Slip", path: "/app/salary-slip" },
      { label: "Department", path: "/masters/department" },
      { label: "Designation", path: "/masters/designation" },
      { label: "Leave Type", path: "/masters/leave-type" },
      { label: "Salary Component", path: "/masters/salary-component" },
    ],
  },
  { index: 5 }
);
