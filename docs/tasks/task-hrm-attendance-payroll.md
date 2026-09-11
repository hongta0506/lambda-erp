# Task: Implement HRM, Attendance & Payroll Module

**Status:** Planned  
**Date:** 2026-09-11  
**Target:** `lambda_erp/hr/`, `lambda_erp/database.py`, `api/`, `frontend/src/`

---

## 1. Mục tiêu (Objective)
Xây dựng phân hệ Quản lý Nhân sự (HRM), Chấm công (Attendance) và Tiền lương (Payroll) tối giản theo kiến trúc của `lambda_erp` (FastAPI + Pydantic + SQLite/PostgreSQL + React Vite), học hỏi mô hình chuẩn từ `frappe/hrms` nhưng không phụ thuộc Frappe framework.

---

## 2. Kiến trúc & Phạm vi nghiệp vụ (Scope)

### Giai đoạn 1: Hồ sơ nhân sự (Core HR)
- **Doctypes / Masters**:
  - `Department` (Phòng ban): code, name, parent_department.
  - `Designation` (Chức danh / Vị trí): designation_name, description.
  - `Employee` (Nhân viên):
    - Mã nhân viên (Naming Series: `EMP-.YYYY.-.#####`).
    - Thông tin cá nhân: first_name, last_name, email, phone, gender, date_of_birth, date_of_joining.
    - Thông tin công việc: department, designation, status (Active, Left, Suspended), company.
    - Thông tin tài khoản nhận lương: bank_name, bank_account_no.

### Giai đoạn 2: Chấm công & Nghỉ phép (Attendance & Leave)
- **Doctypes**:
  - `Leave Type` (Loại nghỉ phép): AL (Annual Leave), SL (Sick Leave), UL (Unpaid Leave), max_days_allowed.
  - `Leave Application` (Đơn xin nghỉ): employee, leave_type, from_date, to_date, total_leave_days, status (Draft, Approved, Rejected).
  - `Attendance` (Điểm danh / Chấm công):
    - employee, attendance_date, status (Present, Absent, On Leave, Half Day).
    - in_time, out_time, working_hours.
    - Naming series: `ATT-.YYYY.-.#####`.

### Giai đoạn 3: Tính lương & Bút toán sổ cái (Payroll & GL Entry)
- **Doctypes**:
  - `Salary Component` (Thành phần lương):
    - name, type (Earning: Lương cơ bản, Phụ cấp; Deduction: BHXH, BHYT, Thuế TNCN, Tạm ứng).
    - default_amount.
  - `Salary Structure` (Cấu trúc lương theo nhân viên hoặc vị trí):
    - employee, earnings (child table), deductions (child table), net_pay.
  - `Salary Slip` (Phiếu lương):
    - Naming series: `SAL-.YYYY.-.#####`.
    - employee, posting_date, start_date, end_date.
    - payment_days, leave_without_pay_days (tự động link từ Attendance & Leave).
    - earnings, deductions, gross_pay, total_deduction, net_pay.
    - Status: Draft, Submitted, Cancelled.
  - **Tích hợp Kế toán (Accounting Integration)**:
    - Khi submit `Salary Slip`, tự sinh `Journal Entry` hoặc `GL Entry`:
      - Nợ: Tài khoản Chi phí lương (`Salary Expenses`).
      - Có: Tài khoản Phải trả người lao động (`Payroll Payable`).
    - Thanh toán qua `Payment Entry` giảm `Payroll Payable` và giảm `Bank/Cash`.

---

## 3. Danh sách file thay đổi & tạo mới

### Backend (`lambda_erp/` & `api/`)
1. `lambda_erp/hr/__init__.py`: Export các Document class.
2. `lambda_erp/hr/department.py`: Controller cho Department.
3. `lambda_erp/hr/employee.py`: Controller cho Employee.
4. `lambda_erp/hr/attendance.py`: Controller cho Attendance.
5. `lambda_erp/hr/leave_application.py`: Controller cho Leave Application.
6. `lambda_erp/hr/salary_structure.py`: Controller cho Salary Structure.
7. `lambda_erp/hr/salary_slip.py`: Controller cho Salary Slip + GL Posting.
8. `lambda_erp/database.py`: Bổ sung DDL `CREATE TABLE IF NOT EXISTS` cho các bảng HR.
9. `api/services.py`: Đăng ký Document classes vào `DOCUMENT_CLASSES`.
10. `api/routers/masters.py`: Đăng ký `employee`, `department` vào danh mục master endpoints.
11. `api/routers/hr.py` (nếu cần endpoint nghiệp vụ chuyên biệt: bulk attendance mark, process payroll).

### Frontend (`frontend/src/`)
1. `frontend/src/lib/doctypes.ts`: Định nghĩa schema form, columns cho Attendance, Leave Application, Salary Structure, Salary Slip.
2. `frontend/src/lib/masters.ts`: Định nghĩa trường dữ liệu cho Employee, Department.
3. `frontend/src/lib/nav.tsx`: Bổ sung menu "Human Resources" (Nhân sự) vào thanh bên Sidebar.
4. `frontend/src/i18n/index.ts`: Bổ sung từ điển song ngữ Việt - Anh cho toàn bộ thuật ngữ nhân sự.

---

## 4. Kế hoạch triển khai chi tiết (Phased Plan)

- **Bước 1**: Viết schema DDL DB trong `lambda_erp/database.py` và model classes trong `lambda_erp/hr/`.
- **Bước 2**: Tích hợp backend service trong `api/services.py` và `api/routers/masters.py`.
- **Bước 3**: Viết test cases tự động (`tests/test_hr.py`) kiểm tra: tạo nhân viên -> chấm công -> xin nghỉ phép -> tạo phiếu lương -> submit hạch toán GL Entry.
- **Bước 4**: Tích hợp UI Frontend (Doctype schemas, Sidebar Nav, i18n Anh - Việt).
- **Bước 5**: Kiểm thử toàn diện trên cả Docker Compose (PostgreSQL) và SQLite local.
